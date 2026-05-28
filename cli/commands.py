import os
from decimal import Decimal
from cli.base import Command
from infra.provision import provision_services
from services import S3Manager, DynamoDBManager
from utils.csv_to_json import to_json


class DeployCommand(Command):
    @property
    def name(self) -> str:
        return "Deploy Infrastructure"

    def __init__(self, factory):
        self.factory = factory

    def execute(self) -> None:
        print("\n[Provisioning] Starting AWS service deployment...")
        try:
            provision_services(self.factory)
            print("[Success] Infrastructure deployed successfully!")
        except Exception as e:
            print(f"[Error] Deployment failed: {e}")


class UploadCommand(Command):
    @property
    def name(self) -> str:
        return "Upload Data"

    def __init__(self, s3_manager: S3Manager):
        self.s3 = s3_manager

    def execute(self) -> None:
        file_path = input("\nEnter the path to the CSV or JSON file: ").strip()

        if not file_path or not os.path.exists(file_path):
            print(f"[Error] File not found: {file_path}")
            return

        print(f"[Uploading] Processing {file_path}...")
        try:
            if file_path.endswith(".json"):
                self.s3.upload_file(file_path)
                print(f"[Success] Uploaded {file_path} to S3.")
            elif file_path.endswith(".csv"):
                json_file_path = file_path.replace(".csv", ".json")
                print("[Processing] Converting CSV to JSON...")
                to_json(file_path, json_file_path)
                self.s3.upload_file(json_file_path)
                print(f"[Success] Converted and uploaded {json_file_path} to S3.")
            else:
                print("[Error] Invalid format. Please provide a .json or .csv file.")
        except Exception as e:
            print(f"[Error] Upload failed: {e}")


class StatusCommand(Command):
    @property
    def name(self) -> str:
        return "View Status/Records"

    def __init__(self, db_manager: DynamoDBManager):
        self.db = db_manager

    def execute(self) -> None:
        limit_str = input(
            "\nHow many recent records do you want to view? (default 5): "
        ).strip()
        limit = int(limit_str) if limit_str and limit_str.isdigit() else 5

        print(f"[Fetching] Retrieving up to {limit} records from DynamoDB...")
        try:
            response = self.db.scan_table(limit=limit)
            items = response.get("Items", [])

            if not items:
                print("[Info] No records found in the database.")
                return

            print("\n--- Student Performance Records ---")
            print(f"{'Student ID':<15} | {'Score':<6} | {'Grade':<5} | {'Attnd%':<7} | {'Hours':<6} | {'Category':<12}")
            print("-" * 75)
            for item in items:
                sid = item.get("student_id", "N/A")
                score = str(item.get("total_score", "N/A"))
                grade = item.get("grade", "N/A")
                attnd = str(item.get("attendance_percentage", "N/A"))
                hours = str(item.get("weekly_self_study_hours", "N/A"))
                cat = item.get("performance_category", "N/A")
                print(f"{sid:<15} | {score:<6} | {grade:<5} | {attnd:<7} | {hours:<6} | {cat:<12}")
            print("-" * 75)

        except Exception as e:
            print(f"[Error] Failed to fetch records: {e}")


class QueryCommand(Command):
    @property
    def name(self) -> str:
        return "Query Student Record"

    def __init__(self, db_manager: DynamoDBManager):
        self.db = db_manager

    def execute(self) -> None:
        student_id = input("\nEnter Student ID to query: ").strip()
        if not student_id:
            print("[Error] Student ID cannot be empty.")
            return

        print(f"[Querying] Searching for student {student_id}...")
        try:
            response = self.db.get_records({"student_id": student_id})
            item = response.get("Item")

            if not item:
                print(f"[Info] No record found for Student ID: {student_id}")
                return

            print("\n--- Student Record Found ---")
            for k, v in item.items():
                label = k.replace("_", " ").title()
                print(f"{label:<25}: {v}")
            print("-" * 40)

        except Exception as e:
            print(f"[Error] Query failed: {e}")


class CreateCommand(Command):
    @property
    def name(self) -> str:
        return "Create New Record"

    def __init__(self, db_manager: DynamoDBManager):
        self.db = db_manager

    def execute(self) -> None:
        print("\n--- Enter Student Details ---")
        student_id = input("Student ID: ").strip()
        if not student_id:
            return

        try:
            study_hours = Decimal(input("Weekly Study Hours: "))
            attendance = Decimal(input("Attendance Percentage: "))
            participation = Decimal(input("Class Participation Score: "))
            total_score = Decimal(input("Total Score: "))
            grade = input("Grade (A/B/C/D/F): ").strip().upper()

            if total_score >= 90:
                category = "Excellent"
            elif total_score >= 80:
                category = "Good"
            elif total_score >= 70:
                category = "Average"
            else:
                category = "Poor"

            item = {
                "student_id": student_id,
                "weekly_self_study_hours": study_hours,
                "attendance_percentage": attendance,
                "class_participation": participation,
                "total_score": total_score,
                "grade": grade,
                "performance_category": category,
            }

            self.db.insert_record(item)
            print(f"[Success] Record for {student_id} created.")
        except (ValueError, ArithmeticError, Decimal.InvalidOperation):
            print("[Error] Invalid numeric input.")
        except Exception as e:
            print(f"[Error] Failed to create record: {e}")


class UpdateCommand(Command):
    @property
    def name(self) -> str:
        return "Update Record"

    def __init__(self, db_manager: DynamoDBManager):
        self.db = db_manager

    def execute(self) -> None:
        student_id = input("\nEnter Student ID to update: ").strip()
        if not student_id:
            return

        print("\nAvailable fields to update:")
        fields = {
            "1": "weekly_self_study_hours",
            "2": "attendance_percentage",
            "3": "class_participation",
            "4": "total_score",
            "5": "grade",
        }
        for k, v in fields.items():
            print(f"{k}. {v.replace('_', ' ').title()}")

        choice = input("Select field to update: ").strip()
        if choice not in fields:
            print("[Error] Invalid choice.")
            return

        field_name = fields[choice]
        new_value_raw = input(f"Enter new value for {field_name}: ").strip()

        try:
            # Convert to appropriate type
            if field_name in [
                "weekly_self_study_hours",
                "attendance_percentage",
                "class_participation",
                "total_score",
            ]:
                new_value = Decimal(new_value_raw)
            else:
                new_value = new_value_raw

            update_expr = f"SET {field_name} = :val"
            attr_values = {":val": new_value}

            # If updating total_score, we should also update category
            if field_name == "total_score":
                score = float(new_value_raw)
                if score >= 90:
                    cat = "Excellent"
                elif score >= 80:
                    cat = "Good"
                elif score >= 70:
                    cat = "Average"
                else:
                    cat = "Poor"
                update_expr += ", performance_category = :cat"
                attr_values[":cat"] = cat

            self.db.update_record({"student_id": student_id}, update_expr, attr_values)
            print(f"[Success] {field_name} updated for student {student_id}.")
        except Exception as e:
            print(f"[Error] Update failed: {e}")


class DeleteCommand(Command):
    @property
    def name(self) -> str:
        return "Delete Record"

    def __init__(self, db_manager: DynamoDBManager):
        self.db = db_manager

    def execute(self) -> None:
        student_id = input("\nEnter Student ID to delete: ").strip()
        if not student_id:
            return

        confirm = (
            input(f"Are you sure you want to delete student {student_id}? (y/n): ")
            .strip()
            .lower()
        )
        if confirm != "y":
            print("[Cancelled] Deletion aborted.")
            return

        try:
            self.db.delete_record({"student_id": student_id})
            print(f"[Success] Record for {student_id} deleted.")
        except Exception as e:
            print(f"[Error] Deletion failed: {e}")
