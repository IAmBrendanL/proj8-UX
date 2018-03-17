import acp_times
import forms
import arrow
import base64
import config
import flask
import logging
import pymongo
import flask_login
from Auth.password import hash_password, verify_password
from Auth.testToken import generate_auth_token, verify_auth_token
from user import User
from flask_restful import Resource, Api
from urllib.parse import urlparse, urljoin
from datetime import timedelta

###
# Globals
###
app = flask.Flask(__name__)
CONFIG = config.configuration()
app.secret_key = CONFIG.SECRET_KEY
client = pymongo.MongoClient("db", 27017)
db = client.btimes
api = Api(app)
login_manager = flask_login.LoginManager()
login_manager.init_app(app)
login_manager.login_view = "/login"


###
# Pages
###
@app.route("/")
@app.route("/index")
@flask_login.login_required
def index():
    app.logger.debug("Main page entry")
    return flask.render_template('calc.html')


@app.route("/display-brevets")
@flask_login.login_required
def display_brevets():
    """
    Displays all brevet records stored in the database
    """
    records = []
    for item in db.btimes.find():
        # convert times to readable format
        item["open"] = arrow.get(item["open"]).format("ddd M/D H:mm")
        item["close"] = arrow.get(item["close"]).format("ddd M/D H:mm")
        records.append(item)
    return flask.render_template("display-brevets.html", records=records)


@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found")
    flask.session['linkback'] = flask.url_for("index")
    return flask.render_template('404.html'), 404


@app.route("/register")
def register():
    form = forms.AuthorizeForm()
    return flask.render_template("register.html", form=form)


@app.route("/token", methods=["GET", "POST"])
def get_token_ui():
    form = forms.AuthorizeForm()
    if form.validate_on_submit():
        user = User.validate_user(form.username.data, form.password.data)
        if user:
            token = generate_auth_token(str(user.get_id()), app.secret_key, 15).decode(encoding="utf-8")
            return flask.jsonify({"token": token, "duration": 15})
    return flask.render_template("authorize.html", form=form)


@app.route("/register_user", methods=["GET", "POST"])
def register_new_user():
    form = forms.LoginForm()
    if form.validate_on_submit():
        user = User.register_user(form.username.data, form.password.data)
        if user:
            result = flask_login.login_user(user=user, remember=form.remember_me.data,
                                            duration=timedelta(days=7))
            next = flask.request.args.get("next")
            if not is_safe_url(next):
                return flask.abort(400)
            return flask.redirect(next or flask.url_for('index'))
    return flask.render_template("register_user.html", form=form)



@app.route("/login", methods=["GET", "POST"])
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        user = User.validate_user(form.username.data, form.password.data)
        if user:
            result = flask_login.login_user(user=user, remember=form.remember_me.data,
                                            duration=timedelta(days=7))
            next = flask.request.args.get("next")
            if not is_safe_url(next):
                return flask.abort(400)
            return flask.redirect(next or flask.url_for('index'))
    return flask.render_template("login.html", form=form)

@app.route("/logout")
@flask_login.login_required
def logout():
    flask_login.logout_user()
    return flask.render_template("/logout_success.html")



def is_safe_url(target):
    ref_url = urlparse(flask.request.host_url)
    test_url = urlparse(urljoin(flask.request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc


@login_manager.user_loader
def load_user(user_id):
    return User.get_user_by_id(user_id)

###############
#
# AJAX request handlers
#   These return JSON, rather than rendering pages.
#
###############
@app.route("/_calc_times")
def _calc_times():
    """
    Calculates open/close times from miles, using rules
    described at https://rusa.org/octime_alg.html.
    Expects one URL-encoded argument, the number of miles.
    """
    app.logger.debug("Got a JSON request")
    # get values
    km = flask.request.args.get('km', 999, type=float)
    brev_dist = flask.request.args.get('dist', 0, type=float)
    begin = flask.request.args.get('begin', arrow.now().isoformat(), type=str)
    # compute values and return results
    open_time = acp_times.open_time(km, brev_dist, begin)
    close_time = acp_times.close_time(km, brev_dist, begin)

    return flask.jsonify(result={"open": open_time, "close": close_time})


#####
# API Methods and helpers
#####
##
# GET Documents APIs and helpers
##
def verify_token_401(token):
    """
    Checks if token is none or not valid and return 401 on true
    """
    if not token or not verify_auth_token(app.secret_key, token.encode(encoding="utf-8")):
        flask.abort(401)


def getKDocuments(sortField=None, k=None, open_time=False, close_time=False):
    """
    Gets k documents from the database sorted by sortField and excludes the mongodb id
    If k is none all documents are retrieved
    If sortField is none the data is unsorted
    If open_time is not True no open times are returned
    If close_time is not True no close times are returned
    """
    # catch k = 0 and set other starting vals
    kBool = True if k is not None else False
    documentsCursor = None
    documents = []

    # Get data out
    if sortField and kBool:
        documentsCursor = db.btimes.find(projection={'_id': False, 'open': True, 'close': True}, limit=k,
                                         sort=[[sortField, pymongo.ASCENDING]])
    elif sortField:
        documentsCursor = db.btimes.find(projection={'_id': False, 'open': True, 'close': True},
                                         sort=([sortField, pymongo.ASCENDING]))
    elif kBool:
        documentsCursor = db.btimes.find(projection={'_id': False, 'open': True, 'close': True}, limit=k)
    else:
        documentsCursor = db.btimes.find(projection={'_id': False, 'open': True, 'close': True})

    # convert data if requested and append
    for item in documentsCursor:
        tmpDict = {}
        if open_time:
            tmpDict["open"] = arrow.get(item["open"]).format("ddd M/D H:mm")
        if close_time:
            tmpDict["close"] = arrow.get(item["close"]).format("ddd M/D H:mm")
        documents.append(tmpDict)
    # return
    return documents


def controle_dict_list_to_CSV(controle_lst, open_time=False, close_time=False):
    """
    Converts a list of condrole dictionaries into a csv string
    """
    outStr = "Open Time,Close Time"
    for item in controle_lst:
        outStr += "\n"
        if open_time and close_time:
            outStr += "{},{}".format(item["open"], item["close"])
        elif close_time:
            outStr += str(item["close"])
        elif open_time:
            outStr += str(item["open"])
    return outStr


class ListAll(Resource):
    def get(self, format="json"):
        """
        Responds to GET requests for all times in json or csv for k times
        """
        verify_token_401(flask.request.args.get('token'))
        k = flask.request.args.get('top')
        k = 0 if k is None else int(k)
        if format == "json":
            return (flask.jsonify({"results": getKDocuments(open_time=True, close_time=True, k=k)}))
        elif format == "csv":
            return (flask.Response(controle_dict_list_to_CSV(getKDocuments(open_time=True, close_time=True, k=k),
                                                             open_time=True, close_time=True), mimetype="/text/csv"))
        else:
            flask.abort(404)


class ListOpen(Resource):
    def get(self, format="json"):
        """
        Responds to GET requests for open times in json or csv for k times
        """
        verify_token_401(flask.request.args.get('token'))
        k = flask.request.args.get('top')
        k = 0 if k is None else int(k)
        if format == "json":
            return (flask.jsonify({"results": getKDocuments(sortField="open", open_time=True, k=k)}))
        elif format == "csv":
            return (flask.Response(controle_dict_list_to_CSV(getKDocuments(open_time=True, k=k), open_time=True),
                                   mimetype="/text/csv"))
        else:
            flask.abort(404)


class ListClose(Resource):
    def get(self, format="json"):
        """
        Responds to GET requests for close times in json or csv for k times
        """
        verify_token_401(flask.request.args.get('token'))
        k = flask.request.args.get('top')
        k = 0 if k is None else int(k)
        if format == "json":
            return (flask.jsonify({"results": getKDocuments(sortField="close", close_time=True, k=k)}))
        elif format == "csv":
            return (flask.Response(controle_dict_list_to_CSV(getKDocuments(close_time=True, k=k), close_time=True),
                                   mimetype="/text/csv"))
        else:
            flask.abort(404)


##
# End Get Documents APIs and helpers
##
##
# User Registration and Access APIs
##
class RegisterUser(Resource):
    def post(self):
        """
        Adds a user to the application and returns their username and id
        If errors in request return 400
        """
        user_name = flask.request.form.get('username')
        passwd = flask.request.form.get('password')
        if not user_name or not passwd:
            app.logger.debug("Got None")
            flask.abort(400)
        elif db.users.find_one({"username": user_name}):
            app.logger.debug("Already Exits")
            flask.abort(400)
        else:
            app.logger.debug("Creating New User")
            _id = str(db.users.insert_one({"username": user_name,
                                           "password_hash": hash_password(passwd)}).inserted_id)
            return flask.make_response(flask.jsonify({"username": user_name, "Location": _id}), 201,
                                       {"Location": "user/" + str(_id)})


class UserToken(Resource):
    def get(self):
        """
        Returns a token for a user via JSON if the user is valid, else 401
        """
        auth = flask.request.headers.get("Authorization").split(" ")

        # abort if malformed auth or if not Basic
        if len(auth) != 2 or auth[0] != "Basic":
            app.logger.debug("Got invalid Authorization Header: {}".format(auth))
            flask.abort(401)
        # decode base64 user:pass, split on ':', and set credentials
        credentials = base64.b64decode(auth[-1]).decode(encoding="utf-8").split(":")
        user_name, passwd = credentials[0], credentials[1]
        app.logger.debug("Auth: {}".format(credentials))

        if not user_name or not passwd:
            app.logger.debug("Got None")
            flask.abort(401)
        else:
            user = db.users.find_one({"username": user_name})
            # check if user exists
            if not user:
                app.logger.debug("Username Not Found")
                flask.abort(401)
            elif verify_password(passwd, user["password_hash"]):
                token = generate_auth_token(str(user['_id']), app.secret_key, 15).decode(encoding="utf-8")
                return flask.jsonify({"token": token, "duration": 15})
            else:
                flask.abort(401)


##
# User Registration and Access APIs
##

#############
# DB saving
#############
@app.route("/save-brevets", methods=["POST"])
def save_brevets():
    """
    Saves brevets to db from post
    """
    kms = flask.request.form.getlist("km")
    locations = flask.request.form.getlist("location")
    open_times = flask.request.form.getlist("open")
    close_times = flask.request.form.getlist("close")
    notes = flask.request.form.getlist("notes")

    # check valid km and insert documents
    empty = True
    for km, loc, open_time, close_time, note in zip(kms, locations, open_times, close_times, notes):
        if km != "":
            empty = False
            open_datetime = arrow.get(open_time, "ddd M/D H:mm")
            close_datetime = arrow.get(close_time, "ddd M/D H:mm")
            db.btimes.insert_one({'dist': float(km), 'location': loc, "open": open_datetime.datetime,
                                  "close": close_datetime.datetime, "note": note})

    # check conditions and flash appropriate message
    if empty:
        flask.flash("Nothing Saved: Form cannot be empty", category="text-danger")
    else:
        flask.flash("Controle points saved", category="text-success")
    # return
    return flask.redirect("/")


###
# REST API routes
###
api.add_resource(ListAll, "/listAll", "/listAll/<format>")
api.add_resource(ListOpen, "/listOnlyOpen", "/listOnlyOpen/<format>")
api.add_resource(ListClose, "/listOnlyClose", "/listOnlyClose/<format>")
api.add_resource(RegisterUser, "/api/register")
api.add_resource(UserToken, "/api/token")

###
# Main and Miscellany
###

app.debug = CONFIG.DEBUG
if app.debug:
    app.logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    print("Opening for global access on port {}".format(CONFIG.PORT))
    app.run(port=CONFIG.PORT, host="0.0.0.0")
