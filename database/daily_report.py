import os
import sys
import logging
from pymongo import MongoClient
import pandas as pd
from datetime import datetime, timedelta

# -------------------------------
# Setup Logging  🔹 CHANGED
# -------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

# -------------------------------
# MongoDB Connection  🔹 CHANGED
# -------------------------------
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")  # default to localhost for host execution
DB_NAME = "sentimentDB"
RAW_COLLECTION = "social_media_posts"
REPORT_COLLECTION = "tweets"  

try:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    raw_collection = db[RAW_COLLECTION]
    report_collection = db[REPORT_COLLECTION]
    logging.info(f"✅ Connected to MongoDB at {MONGO_URI}")
except Exception as e:
    logging.error(f"❌ Failed to connect to MongoDB: {e}")
    sys.exit(1)

# -------------------------------
# Define date range (last 24 hours)
# -------------------------------
now = datetime.utcnow()  # 🔹 CHANGED: use UTC
yesterday = now - timedelta(days=1)
logging.info(f"📅 Generating report for range: {yesterday} → {now}")

# -------------------------------
# Fetch data
# -------------------------------
try:
    data = list(raw_collection.find({"timestamp": {"$gte": yesterday}}))
except Exception as e:
    logging.error(f"❌ Error fetching data: {e}")
    sys.exit(1)

if len(data) == 0:
    logging.warning("No posts found in the last 24 hours.")
    sys.exit(0)

# -------------------------------
# Data processing
# -------------------------------
df = pd.DataFrame(data)

# 🔹 CHANGED: Normalize timestamp strings if stored as str
if df["timestamp"].dtype == "O":
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

# 🔹 CHANGED: Filter by chosen topics
chosen_topics = ["AI", "Cricket", "Movies", "Education",
                 "Technology", "Politics", "Health", "ClimateChange"]
df = df[df["topic"].isin(chosen_topics)]

if df.empty:
    logging.warning("No posts found for selected topics.")
    sys.exit(0)

# -------------------------------
# Compute Summary
# -------------------------------
sentiment_summary = df["sentiment"].value_counts().to_dict()
topic_summary = df["topic"].value_counts().reindex(chosen_topics, fill_value=0).head(5).to_dict()

report = {
    "date": now.strftime("%Y-%m-%d"),
    "generated_at": now.isoformat(),
    "total_posts": len(df),
    "sentiment_summary": sentiment_summary,
    "top_topics": topic_summary
}

# -------------------------------
# Print and Save Report
# -------------------------------
logging.info("📊 Daily Sentiment & Trend Report")
logging.info("--------------------------------")
logging.info(f"Total Posts: {report['total_posts']}")
for s, c in sentiment_summary.items():
    logging.info(f"  {s.capitalize()}: {c}")
logging.info("\nTop Topics:")
for t, c in topic_summary.items():
    logging.info(f"  {t}: {c}")

try:
    report_collection.insert_one(report)
    logging.info("✅ Report saved to MongoDB collection 'daily_reports'.")
except Exception as e:
    logging.error(f"❌ Failed to insert report: {e}")
