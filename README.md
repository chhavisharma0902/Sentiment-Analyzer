💬 Real-Time Sentiment Analyzer with Automated Daily Reports
🧠 Overview
This project is a real-time sentiment analysis system that simulates social media activity using the Faker library. It processes live data streams, performs NLP-based sentiment analysis, extracts trending topics, stores results in MongoDB, and generates automated daily reports using Apache Airflow.

It’s a complete end-to-end pipeline built for educational and research purposes — demonstrating how real-world sentiment monitoring systems work.

🧱 System Architecture
Faker Post Generator → Kafka Producer → Kafka Consumer (BERT + Topic Extraction)
                                           ↓
                                        MongoDB
                                           ↓
                             Streamlit Dashboard (Live View)
                                           ↓
                             Airflow DAG (Daily Reports)

🛠️ Tech Stack

Language: Python

Data Generator: Faker

Stream Processing: Apache Kafka

Database: MongoDB

Sentiment Model: BERT (cardiffnlp/twitter-roberta-base-sentiment)

Dashboard: Streamlit

Automation & Scheduling: Apache Airflow

Libraries: transformers, pandas, textblob, faker, sklearn

🚀 How It Works

Faker generates a continuous stream of posts with random users, topics, and text.

The Kafka Producer sends these posts into a topic.

The Kafka Consumer reads each post, performs:

Sentiment analysis using the BERT model

Topic extraction

Then stores the processed results in MongoDB

The Streamlit Dashboard shows live visual updates of sentiment and trending topics.

Each night, Apache Airflow runs a scheduled DAG that:

Summarizes all posts from the previous day

Calculates sentiment distribution and top trending topics

Inserts the report into a daily_reports MongoDB collection.
