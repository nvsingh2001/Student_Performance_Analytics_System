import boto3
from config import TABLE_NAME, AWS_REGION
from infra.client_factory import AWSClientFactory

def wipe():
    factory = AWSClientFactory(AWS_REGION)
    db = factory.get_dynamodb_table(TABLE_NAME)
    scan = db.scan()
    with db.batch_writer() as batch:
        for each in scan.get('Items', []):
            batch.delete_item(Key={'student_id': each['student_id']})
    print("Table wiped.")

if __name__ == "__main__":
    wipe()
