import yaml

class Honeypot():
    def __init__(self, id:str, owner:str, health:str, last_update:int=None, type:str=None) -> None:
        self.id = id
        self.owner = owner
        self.health = health
        self.last_update = last_update
        self.type = type


class VPS(Honeypot):
    def __init__(self, id:str, owner:str, health:str, last_update:str=None,
                    os:str=None) -> None:
        self.os = os
        Honeypot.__init__(self,
                         id = id,
                         owner = owner,
                         health = health,
                         last_update = last_update,
                         type = "VPS")


def ingest_honeypots(config_file:str) -> None:
    honeypots = []

    with open(config_file, "tr") as fio:
        try:
            config_file = yaml.safe_load(fio)

            for id, config in zip(config_file['servers'],
                                  config_file['servers'].values()):
                honeypots.append(VPS(id,
                    owner = config['owner'],
                    health = config['health'],
                    last_update = config['last-updated'],
                    os = config['os']
                ))

        except yaml.YAMLError as e:
            print(f"Error {e}")

    return honeypots

#types: VPS, Database, Webapplication, NAS, CodeServer

"""
{'servers': 
    {
    '1Cbas2ZWQ8Kq': {'type': 'VPS', 'owner': 'nathaniel@singer.cloud', 'health': 'Healthy', 'last-updated': 1651993737, 'os': 'Ubuntu 20.04'},

    'w8w5t32JFMzT': {'type': 'VPS', 'owner': 'nathaniel@singer.cloud', 'health': 'Healthy', 'last-updated': 1651993737, 'os': 'Ubuntu 20.04'},

    'hFc8c7Hhr8wj': {'type': 'VPS', 'owner': 'nathaniel@singer.cloud', 'health': 'Healthy', 'last-updated': 1651993737, 'os': 'Ubuntu 20.04'}, 

    'PG4f8DE87v7U': {'type': 'VPS', 'owner': 'nathaniel@singer.cloud', 'health': 'Healthy', 'last-updated': 1651993737, 'os': 'Ubuntu 20.04'}
    }
}
"""