from config import BUCKET_NAME
from infra.provision import provision_services
from services import S3Manager
from utils import to_json


def main():
    aws = provision_services()

    # Upload files s3 bucket
    s3 = S3Manager(aws.get_s3(), BUCKET_NAME)

    file_path = input("Enter the path of the file to upload: ")
    if file_path.endswith(".json"):
        s3.upload_file(file_path)
    elif file_path.endswith(".csv"):
        json_file_path = file_path.replace(".csv", ".json")
        to_json(file_path, json_file_path)
        s3.upload_file(json_file_path)
    else:
        print("Invalid file format. Please upload a .json or .csv file.")


if __name__ == "__main__":
    main()
