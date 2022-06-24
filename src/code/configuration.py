import yaml
import os

class Configuration:
    def __init__(self, config_file_relpath:str) -> None:
        # Store the config file path
        if os.path.exists(config_file_relpath):
            self.config_file_relpath = config_file_relpath
        else: 
            print(f"Error: config file does not exist at ./{config_file_relpath}")
            raise FileNotFoundError

        # Read in configuration on init, this is probably sane
        self.read_configuration()

    def read_configuration(self): 
        try:
            with open(self.config_file_relpath) as fio:
                config_fio_handler = yaml.safe_load(fio)
                
                self.tls_enabled = config_fio_handler['tls']['enabled']
                self.private_key_relpath = config_fio_handler['tls']['privatekey_relpath']
                self.public_key_relpath = config_fio_handler['tls']['publickey_relpath']

        except Exception as e:
            print(f"Unhandled error: '{e}'")

    """ In this configuration we only read keys if the path exists and do not raise an exception.
    This means that we may have a None type error if a private key is read. In this case the private
    keys should only exist on the orchestrator or a mTLS client, although on that client it should
    be a unique private key. Therefore this logic should theoretically never error """
    def read_keys(self):
        if os.path.exists(self.public_key_relpath):
            with open(self.public_key_relpath, "rt") as fio: self.public_key = fio.read()
            
        if os.path.exists(self.private_key_relpath):
            with open(self.private_key_relpath, "rt") as fio: self.private_key = fio.read()

    """ Might implement this later tbd if dyamic updates are actually necessary"""
    def write_configuration(self): pass