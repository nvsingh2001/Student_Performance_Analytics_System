import boto3


class AWSProvisioning:
    def __init__(self, region):

        self.dynamodb = boto3.resource("dynamodb", region_name=region)

        self.table = None

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

        self.table = self.dynamodb.create_table(
            TableName=table_name,
            KeySchema=key_schema,
            AttributeDefinitions=attribute_definitions,
            BillingMode=billing_mode,
        )

        print("Creating table...")

        self.table.wait_until_exists()

        self.table.reload()

        print("Table Status:", self.table.table_status)

        return self.table
