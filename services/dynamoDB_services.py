class DynamoDBManager:
    def __init__(self, table_resource):
        self.table = table_resource

    def insert_record(self, item):
        try:
            self.table.put_item(Item=item)
        except Exception as e:
            print(f"Error inserting record: {e}")

    def get_records(self, key):
        try:
            return self.table.get_item(Key=key)
        except Exception as e:
            print(f"Error fetching record: {e}")
            return {}

    def update_record(self, key, update_expression, expression_attribute_values):
        try:
            self.table.update_item(
                Key=key,
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attribute_values,
            )
        except Exception as e:
            print(f"Error updating record: {e}")

    def delete_record(self, key):
        try:
            self.table.delete_item(Key=key)
        except Exception as e:
            print(f"Error deleting record: {e}")

    def scan_table(self, limit=10):
        try:
            return self.table.scan(Limit=limit)
        except Exception as e:
            print(f"Error scanning table: {e}")
            return {}

    def filter_records(self, filter_expression, expression_attribute_values):
        try:
            return self.table.scan(
                FilterExpression=filter_expression,
                ExpressionAttributeValues=expression_attribute_values,
            )
        except Exception as e:
            print(f"Error filtering records: {e}")
            return {}

    def query_index(
        self,
        index_name,
        key_condition_expression,
        expression_attribute_values,
        scan_index_forward=False,
        limit=None,
    ):
        try:
            kwargs = {
                "IndexName": index_name,
                "KeyConditionExpression": key_condition_expression,
                "ExpressionAttributeValues": expression_attribute_values,
                "ScanIndexForward": scan_index_forward,
            }
            if limit:
                kwargs["Limit"] = limit
            return self.table.query(**kwargs)
        except Exception as e:
            print(f"Error querying index: {e}")
            return {}

    def full_scan_table(self, paginator):
        try:
            return paginator.paginate(TableName=self.table.table_name)
        except Exception as e:
            print(f"Error scanning table: {e}")
            return {}
