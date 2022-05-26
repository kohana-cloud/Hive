from os.path import exists
import yaml, bcrypt


class User():
    def __init__(self, id:int, admin:bool, username:str, email:str, pwhash_salted:str, first:str, last:str, phone:str) -> None:
        self.id = id
        self.username = username
        self.email = email
        self.pwhash_salted = pwhash_salted
        self.administrator = admin
        self.first = first
        self.last = last
        self.phone = phone

    def check_password(self, password:str) -> None:
        return bcrypt.checkpw(password.encode('ascii'), self.pwhash_salted.encode('ascii'))

    def generate_pwhash(self, password:str) -> None:
        return bcrypt.hashpw(password.encode('ascii'), 
            bcrypt.gensalt(self.app.config['BCRYPT_ROUNDS']))


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
                    User(id = id,
                        username = attributes['username'],
                        email = attributes['email'],
                        admin = attributes['admin'],
                        pwhash_salted = attributes['pwhash_salted'],
                        first = attributes['first'],
                        last = attributes['last'],
                        phone = attributes['phone']
                ))
        except AttributeError as e:
            print(f"No users read from disk!")

        except yaml.YAMLError as e:
            print(f"Error {e}")
            
            
    return users
