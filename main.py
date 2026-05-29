from config import AWS_REGION, BUCKET_NAME, TABLE_NAME
from infra.client_factory import AWSClientFactory
from services import S3Manager, DynamoDBManager
from cli.commands import (
    DeployCommand,
    ExportCommand,
    LeaderboardCommand,
    UploadCommand,
    StatusCommand,
    QueryCommand,
    CreateCommand,
    UpdateCommand,
    DeleteCommand,
    FilterQueryCommand,
    GSIQueryCommand,
)
from cli.menu import MenuController


def main():
    factory = AWSClientFactory(AWS_REGION)

    s3_manager = S3Manager(factory.get_s3_client(), BUCKET_NAME)
    db_manager = DynamoDBManager(factory.get_dynamodb_table(TABLE_NAME))
    db_client = factory.get_dynamodb_client()

    commands = [
        DeployCommand(factory),
        UploadCommand(s3_manager),
        StatusCommand(db_manager),
        QueryCommand(db_manager),
        CreateCommand(db_manager),
        UpdateCommand(db_manager),
        DeleteCommand(db_manager),
        FilterQueryCommand(db_manager),
        GSIQueryCommand(db_manager),
        ExportCommand(db_client, db_manager),
        LeaderboardCommand(db_manager),
    ]

    menu = MenuController(commands=commands)

    menu.run()


if __name__ == "__main__":
    main()
