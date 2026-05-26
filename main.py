from setup import AWSProvisioning
from config import TABLE_NAME, AWS_REGION


def main():
    aws = AWSProvisioning(AWS_REGION)

    # Create student_performance DynamoDB table
    TableName = TABLE_NAME
    KeySchema = [{"AttributeName": "student_id", "KeyType": "HASH"}]
    AttributeDefinitions = [{"AttributeName": "student_id", "AttributeType": "S"}]
    BillingMode = "PAY_PER_REQUEST"

    aws.create_table(TableName, KeySchema, AttributeDefinitions, BillingMode)


if __name__ == "__main__":
    main()
