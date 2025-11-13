from pymongo import MongoClient
import pandas as pd
from datetime import datetime, timedelta

# -------------------------------
# Connect to MongoDB
# -------------------------------
client = MongoClient("mongodb://localhost:27017/")
db = client["sentimentDB"]

# -------------------------------
# Collections
# -------------------------------
raw_collection = db["social_media_posts"]  # raw tweets from consumer
report_collection = db["tweets"]           # daily report storage

# -------------------------------
# Define date range (last 24 hours)
# -------------------------------
now = datetime.now()
yesterday = now - timedelta(days=1)

# -------------------------------
# Fetch data from last 24 hours
# -------------------------------
data = list(raw_collection.find({"timestamp": {"$gte": yesterday}}))

# If no data found, try fetching assuming timestamp is stored as string
if len(data) == 0:
    yesterday_str = yesterday.strftime("%Y-%m-%d %H:%M:%S")
    data = list(raw_collection.find({"timestamp": {"$gte": yesterday_str}}))

# -------------------------------
# Check if any data found
# -------------------------------
if len(data) == 0:
    print("No data found for the last 24 hours.")
else:
    df = pd.DataFrame(data)

    # -------------------------------
    # Filter only the 8 chosen topics (matching consumer)
    # -------------------------------
    chosen_topics = ["AI", "Cricket", "Movies", "Education",
                     "Technology", "Politics", "Health", "ClimateChange"]
    df = df[df['topic'].isin(chosen_topics)]

    if len(df) == 0:
        print("No posts found for the selected topics in the last 24 hours.")
    else:
        # --- Sentiment Summary ---
        sentiment_summary = df["sentiment"].value_counts().to_dict()

        # --- Top 5 Trending Topics ---
        topic_summary = df["topic"].value_counts().reindex(chosen_topics, fill_value=0).head(5).to_dict()

        # --- Summary Output ---
        report = {
            "date": now.strftime("%Y-%m-%d"),
            "total_posts": len(df),
            "sentiment_summary": sentiment_summary,
            "top_topics": topic_summary
        }

        # --- Print report ---
        print("📅 Daily Sentiment & Trend Report (Selected Topics)")
        print("--------------------------------")
        print(f"Date: {report['date']}")
        print(f"Total Posts: {report['total_posts']}")
        print("\nSentiment Distribution:")
        for s, c in sentiment_summary.items():
            print(f"  {s.capitalize()}: {c}")

        print("\nTop Trending Topics:")
        for t, c in topic_summary.items():
            print(f"  {t}: {c}")

        # --- Store summary back into MongoDB ---
        report_collection.insert_one(report)
        print("\n✅ Report saved to MongoDB collection 'tweets'.")
