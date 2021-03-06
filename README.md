# Project 8: User interface for authenticated brevet time calculator service with MongoDB and REST APIs
## Author: Brendan Lindsey
### Contact: <firstinitial+lastname>@uoregon.edu
_e.g. John Smith -> jsmith_

Reimplemented RUSA ACP controle time calculator with flask and ajax.
Values are stored in a MongoDB database and can be accessed via REST APIs 
which reqiure tokens generated via HTML Basic Auth.

## ACP controle times

That's "controle" with an 'e', because it's French, although "control"
is also accepted.  Controls are points where   
a rider must obtain proof of passage, and control[e] times are the
minimum and maximum times by which the rider must  
arrive at the location.   

The algorithm for calculating controle times is described at
https://rusa.org/octime_alg.html .  Additional background information
is in https://rusa.org/pages/rulesForRiders . 

This replaces the calculator at
https://rusa.org/octime_acp.html . 

## Launching and using proj8-UX
Before running, install the latest versions of docker and docker-compose

* Build the app image using the following command while in the DockerRestAPI directory.
  ~~~
  docker-compose up
  ~~~
  
* Launch http://127.0.0.1:5001 using web browser 
* You will be directed to the login screen where you can login with a previously defined user or register a new one
* Select the distance of the brevet from the "Distance" drop-down menu in the upper, left-hand corner of the page
* Enter the time and date of the event in the upper, right-hand corner of the page
* Enter the distance that the controle point is supposed to be at. 
    * Distances can be entered in either miles or kilometers in their respective columns (found on the left-hand side of the page)
* Add location and notes if desired


## Before Accessing APIs
* _Before_ Accessing the APIs below users must sign up. This can be done either via GUI or by sending a POST request to:
  ~~~
  "http://<host:port>/api/register" 
  ~~~
  The POST request must contain a username and password field denoted by:
  ~~~
  "username=<user_entered_username>"   Brackets denote placeholders

  "password=<user_entered_password>"   Brackets denote placeholders
  ~~~
  The GUI can be accessed at either of the following depending on what you are looking for:
  ~~~
  "http://<host:port>/register_user"   This is entirely GUI driven and will return to the index
  
  "http://<host:port>/register"        This will return the exact same JSON as /api/request
  ~~~
 
* Registered users can then generate a token that MUST be included as an argument in ALL API calls listed after this one.
  A token is valid for 15 seconds and can be generated either via GUI at "http://<host:port>/token" by using HTML Basic AUTH with a GET request to:
  ~~~
   "http://<host:port>/api/token" 
  ~~~
  A token can also be generated via GUI at:
  ~~~
  "http://<host:port>/token"   
  ~~~  
  JSON data is returned with two field:
  ~~~
  "duration": 15 

  "token": "<some_generated_token>     Brackets denote placeholders
  ~~~


##  Accessing APIs
All APIs below require an paramater included in each get request that holds a token generated as decribed in the "Before Accessing APIs" section. For example:
  ~~~
  "http://<host:port>/listAll?token=<some_user_generated_token>" Brackets denote placeholders
  ~~~

The general API spec is as follows:
* Generic APIs that return JSON Data on GET request:
  ~~~
  "http://<host:port>/listAll"  return all open and close times in the database
   
   "http://<host:port>/listOpenOnly"  return open times only
   
   "http://<host:port>/listCloseOnly"  return close times only
   ~~~

* Two different representations: one in CSV and one 
 in JSON can be explicitly accessed as follows:
   ~~~
   "http://<host:port>/listAll/csv"  returns all open and close times in CSV format
   
   "http://<host:port>/listOpenOnly/csv"  returns open times only in CSV format
   
   "http://<host:port>/listCloseOnly/csv"  returns close times only in CSV format

   "http://<host:port>/listAll/json"  returns all open and close times in JSON format
   
   "http://<host:port>/listOpenOnly/json"  retreturnsurn open times only in JSON format
   
   "http://<host:port>/listCloseOnly/json"  returns close times only in JSON format
   ~~~

* A query parameter to get top "k" of any type can be added
   ~~~
   "http://<host:port>/listOpenOnly/csv?top=3"  returns top 3 open times only (in ascending order) in CSV format 
   
   "http://<host:port>/listOpenOnly/json?top=5"  returns top 5 open times only (in ascending order) in JSON format
   ~~~
    
    
## Things to be aware of
* Form data is only validated on the client side
    * This could have been done by recomputing the brevet distance from the sent km and checking the result
    * It is assumed that there is little to no reason for someone to edit the html to insert non-valid times. If this was not an assignment and instead for general use I would have implemented it anyway

# Note about time calculations:
An effort was made to match the orignial calculator's output exactly. This lead to the observation that times are calculated by taking the sum of hours it takes to travel the distance in each bracket (ie 300km race -> (200/speed of 0-200 braket) + (100/speed of the 200-400 bracket)). Each interval was taken to be on the range \[start,end). This works well with the fact that 0 is a special case with a specified start of whenever the event starts and an end time of star + 1 hour. 
