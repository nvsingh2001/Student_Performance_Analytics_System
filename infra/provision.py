import json
import time
import zipfile
from config import BUCKET_NAME, LAMBDA_NAME, ROLE_NAME, TABLE_NAME, AWS_REGION
from .client_factory import AWSClientFactory


class InfrastructureProvisioner:
    def __init__(self, factory: AWSClientFactory):
        self.factory = factory
        self.table = None

    def create_table(self, table_name, key_schema, attribute_definitions, billing_mode):
        db_resource = self.factory.get_dynamodb_resource()
        try:
            self.table = db_resource.create_table(
                TableName=table_name,
                KeySchema=key_schema,
                AttributeDefinitions=attribute_definitions,
                BillingMode=billing_mode,
            )
            print("Creating table...")
            self.table.wait_until_exists()
            self.table.reload()
            print("Table Status:", self.table.table_status)
        except db_resource.meta.client.exceptions.ResourceInUseException:
            print("Table already exists.")
            self.table = db_resource.Table(table_name)

    def create_lambda_role(self, role_name):
        print("Creating IAM role for lambda...")
        iam = self.factory.get_iam_client()
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
            response = iam.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
            )
            role_arn = response["Role"]["Arn"]
            print("Role ARN:", role_arn)
        except iam.exceptions.EntityAlreadyExistsException:
            role_arn = iam.get_role(RoleName=role_name)["Role"]["Arn"]
            print("Role ARN:", role_arn)

        policies = [
            "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess",
            "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess",
            "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
        ]

        for policy in policies:
            iam.attach_role_policy(RoleName=role_name, PolicyArn=policy)
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
        lmb = self.factory.get_lambda_client()
        with open(zip_path, "rb") as f:
            zip_bytes = f.read()
        try:
            response = lmb.create_function(
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
        except lmb.exceptions.ResourceConflictException:
            print("  Function exists, updating code...")
            response = lmb.update_function_code(
                FunctionName=lambda_name, ZipFile=zip_bytes
            )
            lambda_arn = response["FunctionArn"]
            print(f"  Lambda updated: {lambda_arn}")
        return lambda_arn

    def create_s3_bucket(self, bucket_name):
        print(f"Creating S3 bucket: {bucket_name}")
        s3 = self.factory.get_s3_client()
        try:
            s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={"LocationConstraint": self.factory.region},
            )
            print(f"Bucket {bucket_name} created.")
        except s3.exceptions.BucketAlreadyOwnedByYou:
            print(f"Bucket {bucket_name} already exists.")

    def attach_s3_trigger(self, bucket_name, lambda_name, lambda_arn):
        print("Attaching S3 trigger...")
        lmb = self.factory.get_lambda_client()
        s3 = self.factory.get_s3_client()
        try:
            lmb.add_permission(
                FunctionName=lambda_name,
                StatementId="S3InvokeLambda",
                Action="lambda:InvokeFunction",
                Principal="s3.amazonaws.com",
                SourceArn=f"arn:aws:s3:::{bucket_name}",
            )
            print(" permission granted: S3 -> Lambda")
        except lmb.exceptions.ResourceConflictException:
            print(" permission already exists: S3 -> Lambda")

        s3.put_bucket_notification_configuration(
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
        print(" S3 trigger attached")


def provision_services(factory: AWSClientFactory):
    provisioner = InfrastructureProvisioner(factory)

    KeySchema = [{"AttributeName": "student_id", "KeyType": "HASH"}]
    AttributeDefinitions = [{"AttributeName": "student_id", "AttributeType": "S"}]

    provisioner.create_table(
        TABLE_NAME, KeySchema, AttributeDefinitions, "PAY_PER_REQUEST"
    )
    role_arn = provisioner.create_lambda_role(ROLE_NAME)
    provisioner.create_s3_bucket(BUCKET_NAME)
    zip_path = provisioner.zip_lambda()
    lambda_arn = provisioner.deploy_lambda(role_arn, zip_path, LAMBDA_NAME, TABLE_NAME)
    provisioner.attach_s3_trigger(BUCKET_NAME, LAMBDA_NAME, lambda_arn)

    print("Provisioning complete.")
