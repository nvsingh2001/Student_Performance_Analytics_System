import boto3
from config import TABLE_NAME, AWS_REGION
from infra.client_factory import AWSClientFactory
from services import DynamoDBManager

def test():
    factory = AWSClientFactory(AWS_REGION)
    db = DynamoDBManager(factory.get_dynamodb_table(TABLE_NAME))
    
    print("Scanning table for sample data types...")
    res = db.scan_table(limit=2)
    items = res.get('Items', [])
    for item in items:
        print(f"ID: {item.get('student_id')}")
        print(f"  Attendance Type: {type(item.get('attendance_percentage'))} - Value: {item.get('attendance_percentage')}")
        print(f"  Hours Type: {type(item.get('weekly_self_study_hours'))} - Value: {item.get('weekly_self_study_hours')}")

if __name__ == "__main__":
    test()
