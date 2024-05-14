import json
import os

class Credential():
    def __init__(self):
        dir_name = os.path.dirname(__file__)
        file_path = os.path.join(dir_name,'credential.json')
        with open(file_path, 'r') as myfile:
            data = myfile.read()
        self.obj = json.loads(data)

    def get_telegram_token(self):
        return self.obj["telegram_api_token"]

    def get_username(self):
        return self.obj["username"]

    def get_password(self):
        return self.obj["password"]

    def get_database_name(self):
        return self.obj["database_name"]

    def get_conn_uri(self):
        return "postgresql://%s:%s@127.0.0.1:5432/%s" %(self.get_username(), self.get_password(), self.get_database_name())

    def get_ip_address(self):
        return self.obj["ip_address"]
