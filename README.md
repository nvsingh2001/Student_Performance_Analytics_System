# Student Performance Analytics System

A comprehensive, cloud-native application designed to manage and analyze student performance data using AWS services and a Python-based CLI.

## 🚀 Features

-   **Automated AWS Provisioning**: One-click deployment of DynamoDB tables, S3 buckets, Lambda functions, and IAM roles.
-   **Serverless Data Processing**: AWS Lambda automatically processes student records uploaded to S3, performing:
    -   Data validation and normalization.
    -   Performance categorization (A, B, C, D, F).
    -   "At-Risk" student detection based on attendance and scores.
    -   High-performance batch insertion into DynamoDB.
-   **Advanced CLI Management**:
    -   **Full CRUD**: Create, Read, Update, and Delete student records directly.
    -   **Intelligent Querying**: Filter records and perform high-speed GSI queries for top students by grade.
    -   **Global Leaderboard**: View the top 10 students across all grades using optimized GSI aggregation.
    -   **Data Export**: Export records from DynamoDB to local CSV or JSON files.
-   **Scalable Architecture**: Built with Dependency Injection and a clean service-oriented architecture.

## 🏗️ Architecture

-   **Frontend**: Interactive Python CLI (Menu-driven).
-   **Database**: AWS DynamoDB (with Global Secondary Indexes for performance).
-   **Storage**: AWS S3 (Event-driven trigger).
-   **Compute**: AWS Lambda (Python 3.13).
-   **Infrastructure**: Custom Python provisioning script using Boto3.

## 🛠️ Prerequisites

-   Python 3.12+
-   AWS CLI configured with appropriate credentials.
-   `requirements.txt` dependencies installed.

## 🚦 Getting Started

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/nvsingh2001/Student_Performance_Analytics_System.git
    cd Student_Performance_Analytics_System
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the CLI**:
    ```bash
    python main.py
    ```

4.  **Provision Infrastructure**: Select the **Deploy Infrastructure** option in the CLI menu to set up all required AWS resources.

## 📂 Project Structure

-   `cli/`: Command-line interface logic and menu controllers.
-   `infra/`: AWS client factory and infrastructure provisioning scripts.
-   `lambda/`: Serverless function code for S3-triggered data processing.
-   `services/`: Business logic for S3 and DynamoDB management.
-   `utils/`: Display helpers, file I/O, and shared utilities.
-   `config.py`: Centralized configuration for AWS resource names and regions.
