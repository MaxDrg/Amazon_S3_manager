import os
import json
import boto3
import logging
import datetime
from random import randint
from botocore.exceptions import ClientError

class Bucket_data:
    def __init__(self, name, date, region) -> None:
        self.name = name
        self.date = date
        self.region = region

class File_data:
    def __init__(self, name, last_update, content) -> None:
        self.name = name
        self.date = last_update
        self.content = content

class Amazon:
    def __init__(self, keys) -> None:
        self.client = boto3.client(
            's3',
            aws_access_key_id = keys['aws_access_key_id'],
            aws_secret_access_key = keys['aws_secret_access_key'],
        )

    def create_bucket(self, bucket_name, region_name):
        print(bucket_name)
        print(region_name)
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

    def add_file(self, bucket_name, file_name, data):
        file_path = f"json/buffer{randint(10000, 999999)}.json"
        with open(file_path, "w") as file:
            json.dump(data, file, indent=2)
        try:
            self.client.upload_file(file_path, bucket_name, f"{file_name}.json")
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
            Key=f"{file_name}.json"
        )

    def get_buckets(self):
        data = []
        for bucket in self.client.list_buckets()['Buckets']:
            try:
                data.append(Bucket_data(
                    bucket['Name'], 
                    datetime.datetime.strftime(bucket['CreationDate'], "%d/%m/%y %H:%M"),
                    self.client.get_bucket_location(Bucket=bucket['Name'])['LocationConstraint']
                ))
            except:
                pass
        return data

    def get_files(self, bucket_name):
        data = []
        try:
            for file in self.client.list_objects(Bucket=bucket_name)['Contents']:
                content = self.client.get_object(
                    Bucket = bucket_name,
                    Key = file['Key']
                )
            data.append(File_data(
                file['Key'].split('.')[0], 
                datetime.datetime.strftime(file['LastModified'], "%d/%m/%y %H:%M"),
                json.load(content['Body'])
            ))
        except:
            pass
        return data