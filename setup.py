import boto3
import json
import time
import zipfile
from config import BUCKET_NAME, LAMBDA_NAME, ROLE_NAME, TABLE_NAME, AWS_REGION


class AWSProvisioning:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AWSProvisioning, cls).__new__(cls)
        return cls._instance

    def __init__(self, region):
        if not hasattr(self, "_initialized"):
            self._initialized = True
            self._dynamodb = boto3.resource("dynamodb", region_name=region)
            self._iam = boto3.client("iam", region_name=region)
            self._s3 = boto3.client("s3", region_name=region)
            self._lambda = boto3.client("lambda", region_name=region)
            self._region = region
            self._s3_bucket = None

    def get_table(self):
        return self.table

    def get_s3(self):
        return self._s3

    def get_lambda(self):
        return self._lambda

    def get_iam(self):
        return self._iam

    def create_table(self, table_name, key_schema, attribute_definitions, billing_mode):
        """
        Create student_performance DynamoDB table.

        Attributes:
        - student_id
        - weekly_self_study_hours
        - attendance_percentage
        - class_participation
        - total_score
        - grade
        - performance_category
        """
        try:
            self.table = self._dynamodb.create_table(
                TableName=table_name,
                KeySchema=key_schema,
                AttributeDefinitions=attribute_definitions,
                BillingMode=billing_mode,
            )

            print("Creating table...")

            self.table.wait_until_exists()

            self.table.reload()

            print("Table Status:", self.table.table_status)

        except self._dynamodb.meta.client.exceptions.ResourceInUseException:
            print("Table already exists.")
            self.table = self._dynamodb.Table(table_name)

    def create_lambda_role(self, role_name):
        print("Creating IAM role for lambda...")

        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "lambda.amazonaws.com"},
                    "Action": "sts:AssumeRole",
                }
            ],
        }

        try:
            response = self._iam.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
            )
            role_arn = response["Role"]["Arn"]
            print("Role ARN:", role_arn)
        except self._iam.exceptions.EntityAlreadyExistsException:
            role_arn = self._iam.get_role(RoleName=role_name)["Role"]["Arn"]
            print("Role ARN:", role_arn)

        policies = [
            "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess",
            "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess",
            "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
        ]

        for policy in policies:
            self._iam.attach_role_policy(RoleName=role_name, PolicyArn=policy)
            print(f"  Attached: {policy.split('/')[-1]}")

        print(" Waiting 10s for IAM role to propagate...")

        time.sleep(10)

        return role_arn

    def zip_lambda(self):
        print("Zipping Lambda function...")
        zip_path = "lambda_function.zip"

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zip:
            zip.write("lambda/handler.py", "handler.py")
            zip.write("lambda/utils.py", "utils.py")

        print(f"  Created: {zip_path}")
        return zip_path

    def deploy_lambda(self, role_arn, zip_path, lambda_name, table_name):
        print("Deploying Lambda function...")

        with open(zip_path, "rb") as f:
            zip_bytes = f.read()
        try:
            response = self._lambda.create_function(
                FunctionName=lambda_name,
                Runtime="python3.13",
                Role=role_arn,
                Handler="handler.lambda_handler",
                Code={"ZipFile": zip_bytes},
                Timeout=60,
                MemorySize=256,
                Environment={"Variables": {"TABLE_NAME": table_name}},
            )

            lambda_arn = response["FunctionArn"]
            print(f"  Lambda deployed: {lambda_arn}")
        except self._lambda.exceptions.ResourceConflictException:
            print("  Function exists, updating code...")
            response = self._lambda.update_function_code(
                FunctionName=lambda_name, ZipFile=zip_bytes
            )
            lambda_arn = response["FunctionArn"]
            print(f"  Lambda updated: {lambda_arn}")

        return lambda_arn

    def create_s3_bucket(self, bucket_name):
        print(f"Creating S3 bucket: {bucket_name}")

        try:
            self._s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={"LocationConstraint": self._region},
            )

            print(f"Bucket {bucket_name} created.")
        except self._s3.exceptions.BucketAlreadyOwnedByYou:
            print(f"Bucket {bucket_name} already exists.")

    def attach_s3_trigger(self, bucket_name, lambda_name, lambda_arn):
        print("Attaching S3 trigger...")

        try:
            self._lambda.add_permission(
                FunctionName=lambda_name,
                StatementId="S3InvokeLambda",
                Action="lambda:InvokeFunction",
                Principal="s3.amazonaws.com",
                SourceArn=f"arn:aws:s3:::{bucket_name}",
            )

            print(" permission granted: S3 -> Lambda")

        except self._lambda.exceptions.ResourceConflictException:
            print(" permission already exists: S3 -> Lambda")

        self._s3.put_bucket_notification_configuration(
            Bucket=bucket_name,
            NotificationConfiguration={
                "LambdaFunctionConfigurations": [
                    {
                        "LambdaFunctionArn": lambda_arn,
                        "Events": ["s3:ObjectCreated:*"],
                        "Filter": {
                            "Key": {
                                "FilterRules": [
                                    {"Name": "prefix", "Value": "student_records/"}
                                ]
                            }
                        },
                    }
                ]
            },
        )
        print(" S3 trigger attached - uploads to bucket will trigger Lambda")


def provision_services():
    aws = AWSProvisioning(AWS_REGION)
    KeySchema = [{"AttributeName": "student_id", "KeyType": "HASH"}]
    AttributeDefinitions = [{"AttributeName": "student_id", "AttributeType": "S"}]
    BillingMode = "PAY_PER_REQUEST"

    aws.create_table(TABLE_NAME, KeySchema, AttributeDefinitions, BillingMode)
    role_arn = aws.create_lambda_role(ROLE_NAME)
    aws.create_s3_bucket(BUCKET_NAME)
    zip_path = aws.zip_lambda()
    lambda_arn = aws.deploy_lambda(role_arn, zip_path, LAMBDA_NAME, TABLE_NAME)
    aws.attach_s3_trigger(BUCKET_NAME, LAMBDA_NAME, lambda_arn)

    print("Provisioning complete.")

    return aws
