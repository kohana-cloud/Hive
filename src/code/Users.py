from os.path import exists
import yaml, bcrypt


class User():
    def __init__(self, id:int, admin:bool, username:str, email:str, pwhash_salted:str, first:str, last:str, phone:str) -> None:
        self.id = id
        self.username = username
        self.email = email
        self.pwhash_salted = pwhash_salted
        self.admin = admin
        self.first = first
        self.last = last
        self.phone = phone

    def check_password(self, password:str) -> None:
        return bcrypt.checkpw(password.encode('ascii'), self.pwhash_salted.encode('ascii'))

def generate_pwhash(password:str, bcrypt_rounds:int) -> None:
    return bcrypt.hashpw(password.encode('ascii'), 
        bcrypt.gensalt(bcrypt_rounds)).decode('ascii')


def ingest_users(users_file:str) -> None:
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


def append_user(users_file:str, user:User) -> bool:
    users = ingest_users(users_file)

    # Cannot append at declaration, see: https://stackoverflow.com/questions/16935381/appending-an-item-to-a-python-list-in-the-declaration-statement-list-append
    users.append(user)

    with open(users_file, "tw") as fio:
        try:
            user_write = \
            { "users": 
                { user.id :
                    {
                        "username": user.username,
                        "email": user.email,
                        "pwhash_salted": user.pwhash_salted,
                        "admin": False,
                        "first": user.first,
                        "last": user.last,
                        "phone": user.phone
                    } for user in users
                } 
            }

            yaml.safe_dump(user_write, fio)

            return True

        except yaml.YAMLError as e:
            print(f"Error {e}")

            return False

    return False