import boto3
import json
import os
from utils import calculate_performance_category, validate_record
from decimal import Decimal

s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")
TABLE_NAME = os.environ["TABLE_NAME"]


def convert_floats(obj):
    if isinstance(obj, list):
        return [convert_floats(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_floats(v) for k, v in obj.items()}
    elif isinstance(obj, float):
        return Decimal(str(obj))

    return obj


def insert_into_dynamodb(table, records):
    for record in records:
        table.put_item(Item=record)
        print(f"Inserted: {record['student_id']}")


def lambda_handler(event, context):
    # Get the S3 bucket name and object key from the event
    bucket_name = event["Records"][0]["s3"]["bucket"]["name"]
    object_key = event["Records"][0]["s3"]["object"]["key"]

    # Read the file from s3
    try:
        response = s3.get_object(Bucket=bucket_name, Key=object_key)
        file_content = response["Body"].read().decode("utf-8")
    except Exception as e:
        print(f"Error reading file from S3: {e}")
        raise

    # Parse the file content
    try:
        students = json.loads(file_content)
    except Exception as e:
        print(f"Error parsing file content: {e}")
        raise

    if not isinstance(students, list):
        raise ValueError("JSON file must contain a list of student records")

    print(f"Found {len(students)} records")

    # Calculate performance category
    valid_records = []
    skipped_records = []

    for student in students:
        try:
            validate_record(student)
            student["performance_category"] = calculate_performance_category(
                float(student["total_score"])
            )

            student = convert_floats(student)
            valid_records.append(student)
        except Exception as e:
            print(f"SKIPPING record {student.get('student_id', 'unknown')}: {e}")
            skipped_records.append(student)

    table = dynamodb.Table(TABLE_NAME)

    insert_into_dynamodb(table, valid_records)

    return {
        "statusCode": 200,
        "body": json.dumps(
            {"inserted": len(valid_records), "skipped": len(skipped_records)}
        ),
    }
