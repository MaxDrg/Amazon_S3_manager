from . import models

class Logs:
    def add_bucket(self, bucket_name: str):
        self.del_log()
        models.logs(
            operation = 1,
            bucket_name = bucket_name
        ).save()

    def del_bucket(self, bucket_name: str):
        self.del_log()
        models.logs(
            operation = 2,
            bucket_name = bucket_name
        ).save()

    def add_file(self, bucket_name: str, file_name: str):
        self.del_log()
        models.logs(
            operation = 3,
            bucket_name = bucket_name,
            file_name = file_name
        ).save()

    def del_file(self, bucket_name: str, file_name: str):
        self.del_log()
        models.logs(
            operation = 4,
            bucket_name = bucket_name,
            file_name = file_name
        ).save()

    def change_file(self, bucket_name: str, file_name: str):
        self.del_log()
        models.logs(
            operation = 5,
            bucket_name = bucket_name,
            file_name = file_name
        ).save()

    def del_log():
        if len(models.logs.objects.all()) > 100:
            id = models.logs.objects.all()[0][id]
            models.logs.objects.filter(id = id).delete()