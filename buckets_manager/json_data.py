import json

class Data:
    def __init__(self, file):
        self.file = file

    def get_data(self):
        with open(self.file, "r") as json_data:
            return json.load(json_data)

    def set_data(self, aws_access_key_id, aws_secret_access_key):
        new_data = {
            "aws_access_key_id": aws_access_key_id,
            "aws_secret_access_key": aws_secret_access_key
        }
        with open(self.file, "w") as json_data:
            json.dump(new_data, json_data, indent=2)