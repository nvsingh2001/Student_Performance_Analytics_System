from setup import AWSProvisioning
from config import BUCKET_NAME, LAMBDA_NAME, ROLE_NAME, TABLE_NAME, AWS_REGION


def main():
    aws = AWSProvisioning(AWS_REGION)

    # Creating student_performance DynamoDB table
    TableName = TABLE_NAME
    KeySchema = [{"AttributeName": "student_id", "KeyType": "HASH"}]
    AttributeDefinitions = [{"AttributeName": "student_id", "AttributeType": "S"}]
    BillingMode = "PAY_PER_REQUEST"

    aws.create_table(TableName, KeySchema, AttributeDefinitions, BillingMode)
    role_arn = aws.create_lambda_role(ROLE_NAME)
    aws.create_s3_bucket(BUCKET_NAME)
    zip_path = aws.zip_lambda()
    lambda_arn = aws.deploy_lambda(role_arn, zip_path, LAMBDA_NAME, TableName)
    aws.attach_s3_trigger(BUCKET_NAME, LAMBDA_NAME, lambda_arn)


if __name__ == "__main__":
    main()
