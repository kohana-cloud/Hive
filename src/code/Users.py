import yaml
from os.path import exists
import datetime
import jwt
import bcrypt
import time

class User():
    def __init__(self, app:object, id:int, admin:bool, username:str, email:str, pwhash_salted:str, first:str, last:str, phone:str) -> None:
        self.app = app
        self.id = id
        self.username = username
        self.email = email
        self.pwhash_salted = pwhash_salted
        self.administrator = admin
        self.first = first
        self.last = last
        self.phone = phone
        self.jwt = None

    def __assign_jwt(self): 
        self.jwt = jwt.encode({
            'id'    : self.id,
            'name'  : f"{self.first} {self.last}",
            'iat'   : datetime.datetime.utcnow(),
            'exp'   : datetime.datetime.utcnow() 
                        + datetime.timedelta(minutes=self.app.config['LOGINEXP_MINS'])
            }, self.app.config['SECRET_KEY'], "HS256")
    
    def __update_jwt_exp(self):
        decoded_jwt_timestamp_notvalidated = jwt.decode(
            self.jwt, options={"verify_signature": False})['iat']

        self.jwt = jwt.encode({
            'id'    : self.id,
            'name'  : f"{self.first} {self.last}",
            'iat'   : decoded_jwt_timestamp_notvalidated,
            'exp'   : datetime.datetime.utcnow() 
                        + datetime.timedelta(minutes=self.app.config['LOGINEXP_MINS'])
            }, self.app.config['SECRET_KEY'], "HS256")

    def get_jwt(self):
        # Assign JWT if unassigned
        if (self.jwt == None): self.__assign_jwt()

        # Remove JWT if expired
        decoded_jwt_notvalidated = jwt.decode(self.jwt, options={"verify_signature": False})
        if ((decoded_jwt_notvalidated['exp'] - int(time.time())) < 0):
            self.jwt = None

        # Assign JWT if unassigned
        if (self.jwt == None): self.__assign_jwt()

        # Update expiration timestamp
        self.__update_jwt_exp()

        # Return JWT to caller
        return self.jwt

    def expire_jwt(self): self.jwt = None

    def check_password(self, password:str) -> None:
        return bcrypt.checkpw(password.encode('ascii'), self.pwhash_salted.encode('ascii'))

    def generate_pwhash(self, password:str) -> None:
        return bcrypt.hashpw(
            password.encode('ascii'), 
            bcrypt.gensalt(self.app.config['BCRYPT_ROUNDS'])
        )


def ingest_users(users_file:str, app:object) -> None:
    users = []

    if not (exists(users_file)):
        with open(users_file, "tw") as fio: fio.write("users:\n")
        return

    with open(users_file, "tr") as fio:
        try:
            users_file = yaml.safe_load(fio)

            for id, attributes in zip(users_file['users'],
                                  users_file['users'].values()):
                users.append(
                    User(app = app,
                        id = id,
                        username = attributes['username'],
                        email = attributes['email'],
                        admin = attributes['admin'],
                        pwhash_salted = attributes['pwhash_salted'],
                        first = attributes['first'],
                        last = attributes['last'],
                        phone = attributes['phone']
                ))

        except yaml.YAMLError as e:
            print(f"Error {e}")

    return users
