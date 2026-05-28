import boto3
from decimal import Decimal
from config import TABLE_NAME, AWS_REGION
from infra.client_factory import AWSClientFactory
from services import DynamoDBManager

def test():
    factory = AWSClientFactory(AWS_REGION)
    db = DynamoDBManager(factory.get_dynamodb_table(TABLE_NAME))
    
    print("Testing Query 1 (Attendance > 90)...")
    try:
        res = db.filter_records("attendance_percentage > :val", {":val": Decimal("90")})
        print(f"Found {len(res.get('Items', []))} records.")
    except Exception as e:
        print(f"Error: {e}")
        
    print("Testing Query 2 (Study Hours > 10)...")
    try:
        res = db.filter_records("weekly_self_study_hours > :val", {":val": Decimal("10")})
        print(f"Found {len(res.get('Items', []))} records.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test()
