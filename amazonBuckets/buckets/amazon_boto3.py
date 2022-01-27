import boto3
import datetime
import logging
from botocore.exceptions import ClientError
import os
from random import randint

class Bucket_data:
    def __init__(self, name, date, count, region) -> None:
        self.Name = name
        self.Date = date
        self.Count = count
        self.Region = region

class Json_data:
    def __init__(self, name, last_update) -> None:
        self.Name = name
        self.Date = last_update

class Amazon:
    def __init__(self, keys) -> None:
        self.client = boto3.client(
            's3',
            aws_access_key_id = keys['aws_access_key_id'],
            aws_secret_access_key = keys['aws_secret_access_key'],
        )

    def get_buckets(self):
        data = self.client.list_buckets()
        return data['Buckets']

    def get_buckets_data(self):
        data = []
        for bucket in self.client.list_buckets()['Buckets']:
            length = 0
            try:
                length = len(self.client.list_objects(Bucket=bucket["Name"])['Contents'])
            except:
                pass
            data.append(Bucket_data(bucket["Name"], 
            datetime.datetime.strftime(bucket['CreationDate'], "%d/%m/%y %H:%M"),
            length, self.client.get_bucket_location(Bucket=bucket['Name'])['LocationConstraint']))
        return data

    def get_json(self, bucket_name):
        data = []
        try:
            for json in self.client.list_objects(Bucket=bucket_name)['Contents']:
                data.append(Json_data(json['Key'].split('.')[0], 
                datetime.datetime.strftime(json['LastModified'], "%d/%m/%y %H:%M")))
        except:
            print('Error in get_json/amazon_boto3.py !')
        return data, self.client.get_bucket_location(Bucket=bucket_name)['LocationConstraint']

    def add_new_json(self, bucket_name, file_data):
        import json
        file_path = f"json/buffer{randint(10000, 999999)}.json"
        with open(file_path, "w") as file:
            json.dump(file_data, file, indent=2)
        file_name = 0
        try:
            for json in self.client.list_objects(Bucket=bucket_name)['Contents']:
                if int(json['Key'].split('.')[0]) > file_name:
                    file_name = int(json['Key'].split('.')[0])
        except:
            pass

        try:
            self.client.upload_file(file_path, bucket_name, f"{file_name + 1}.json")
        except ClientError as e:
            logging.error(e)
        os.remove(file_path)

    def delete_bucket(self, bucket_name):
        try:
            for key in self.client.list_objects(Bucket=bucket_name)['Contents']:
                self.client.delete_object(
                Bucket=bucket_name,
                Key=key['Key']
                )
        except:
            pass
        self.client.delete_bucket(
           Bucket=bucket_name
        )

    def delete_file(self, bucket_name, file_name):
        self.client.delete_object(
            Bucket=bucket_name,
            Key=file_name
        )

    def create_bucket(self, bucket_name, region_name):
        import json
        resource = {"Resource": f"arn:aws:s3:::{bucket_name}/*"}

        location = {'LocationConstraint': region_name}
        try:
            self.client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration=location
            )
        except:
            return True
        with open("json/policy.json", "r") as file:
            policy = json.load(file)
        policy['Statement'][0].update(resource)
        self.client.put_bucket_policy(Bucket=bucket_name, Policy=json.dumps(policy))
        return False

    def get_data_from_json(self, bucket_name, key):
        import json
        obj = self.client.get_object(
            Bucket = bucket_name,
            Key = key
        )
        return json.load(obj['Body'])

    def update_json(self, bucket_name, file_data, file_name):
        import json
        file_path = f"json/buffer{randint(10000, 999999)}.json"
        with open(file_path, "w") as file:
            json.dump(file_data, file, indent=2)
        try:
            self.client.upload_file(file_path, bucket_name, f"{file_name}.json")
        except ClientError as e:
            logging.error(e)
        os.remove(file_path)