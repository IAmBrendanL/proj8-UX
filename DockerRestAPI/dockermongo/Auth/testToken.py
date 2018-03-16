import time
from itsdangerous import (TimedJSONWebSignatureSerializer \
                                  as Serializer, BadSignature, \
                                  SignatureExpired)


def generate_auth_token(id, secret, expiration=600):
   s = Serializer(secret, expires_in=expiration)
   # pass index of user
   return s.dumps({'id': id})

def verify_auth_token(secret, token):
    s = Serializer(secret)
    try:
        data = s.loads(token)
    except SignatureExpired:
        return None    # valid token, but expired
    except BadSignature:
        return None    # invalid token
    return "Success"

if __name__ == "__main__":
    t = generate_auth_token(10)
    for i in range(1, 20):
        print(verify_auth_token(t))
        time.sleep(1)
