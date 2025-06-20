# 🎮 Game Pipeline Project

This project builds a full data pipeline that scrapes gameplay data from multiple sources and loads it into a cloud-hosted database using AWS services. It showcases end-to-end data engineering skills using Python, Selenium, AWS Lambda (Dockerized), and Amazon RDS.

## 🧠 Overview

- Scrapes game duration data from [HowLongToBeat.com](https://howlongtobeat.com/)
- Processes and transforms the data with Python (Pandas)
- Deploys scraping logic inside Dockerized AWS Lambda functions
- Loads cleaned data into an Amazon RDS (PostgreSQL) database

## 🔧 Tech Stack

| Component        | Technology         |
|------------------|--------------------|
| Scraping         | Python + Selenium  |
| Orchestration    | AWS Lambda (Docker)|
| Storage          | Amazon RDS         |
| Containerization | Docker             |
| Scripting        | Pandas, Requests   |

## 📂 Project Structure

game_pipeline/ <br>
├── hltb_api_scrape/ # Web scraping scripts for HowLongToBeat <br>
├── selenium-lambda-docker/ # Dockerized Lambda setup for deployment <br>
├── README.md <br>
├── LICENSE <br>
└── .gitignore


## 🚀 Deployment Notes

- Lambda functions are deployed using Docker images to handle dependencies like Selenium and Chromium.
- Configuration allows scraping logic to run serverlessly with scalable deployment via AWS.

## ✅ Key Skills Demonstrated

- Building end-to-end ETL pipelines
- Web scraping with dynamic content (Selenium)
- AWS Lambda deployment with Docker
- Database schema design and PostgreSQL integration
- Cloud-native architecture (serverless)
- Data transformation using Python & Pandas

## 🧪 Future Enhancements

- Add orchestration with Step Functions or Airflow
- Expand scraping to additional game data sources
- Use S3 for intermediate CSV storage
- Add automated tests and monitoring

---

### 👤 Author

Kyle Anderson  
AWS Data Center Technician | Aspiring Data Engineer  
[GitHub](https://github.com/kyleanderson84)

