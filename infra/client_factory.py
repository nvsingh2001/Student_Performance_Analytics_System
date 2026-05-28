import boto3


class AWSClientFactory:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AWSClientFactory, cls).__new__(cls)
        return cls._instance

    def __init__(self, region: str):
        if not hasattr(self, "_initialized"):
            self._initialized = True
            self.region = region
            self._dynamodb_resource = boto3.resource("dynamodb", region_name=region)
            self._dynamodb_client = self._dynamodb_resource.meta.client
            self._s3 = boto3.client("s3", region_name=region)
            self._iam = boto3.client("iam", region_name=region)
            self._lambda = boto3.client("lambda", region_name=region)

    def get_dynamodb_client(self):
        return self._dynamodb_client

    def get_dynamodb_resource(self):
        return self._dynamodb_resource

    def get_dynamodb_table(self, table_name: str):
        return self._dynamodb_resource.Table(table_name)

    def get_s3_client(self):
        return self._s3

    def get_iam_client(self):
        return self._iam

    def get_lambda_client(self):
        return self._lambda
