class S3Manager:
    def __init__(self, s3_client, bucket_name):
        self.s3_client = s3_client
        self.bucket_name = bucket_name

    def upload_file(self, file_path):
        with open(file_path, "rb") as f:
            file_name = "student_records/" + file_path.split("/")[-1]
            self.s3_client.upload_fileobj(f, self.bucket_name, file_name)
