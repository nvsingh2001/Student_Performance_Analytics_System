from config import AWS_REGION, BUCKET_NAME, TABLE_NAME
from infra.client_factory import AWSClientFactory
from services import S3Manager, DynamoDBManager
from cli.commands import (
    DeployCommand,
    UploadCommand,
    StatusCommand,
    QueryCommand,
    CreateCommand,
    UpdateCommand,
    DeleteCommand,
    FilterQueryCommand,
)
from cli.menu import MenuController


def main():
    factory = AWSClientFactory(AWS_REGION)

    s3_manager = S3Manager(factory.get_s3_client(), BUCKET_NAME)
    db_manager = DynamoDBManager(factory.get_dynamodb_table(TABLE_NAME))

    commands = [
        DeployCommand(factory),
        UploadCommand(s3_manager),
        StatusCommand(db_manager),
        QueryCommand(db_manager),
        CreateCommand(db_manager),
        UpdateCommand(db_manager),
        DeleteCommand(db_manager),
        FilterQueryCommand(db_manager),
    ]

    menu = MenuController(commands=commands)

    menu.run()


if __name__ == "__main__":
    main()
