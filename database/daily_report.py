from pymongo import MongoClient
import pandas as pd
from datetime import datetime, timedelta, timezone

# -------------------------------
# Connect to MongoDB
# -------------------------------
client = MongoClient("mongodb://localhost:27017/")
db = client["sentimentDB"]

raw_collection = db["social_media_posts"]
report_collection = db["daily_reports"]   # Better name

# -------------------------------
# Proper UTC alignment
# -------------------------------
now = datetime.now(timezone.utc)
yesterday = now - timedelta(days=1)

# -------------------------------
# Fetch last 24 hours data (timestamps stored as datetime)
# -------------------------------
data = list(raw_collection.find({
    "timestamp": {"$gte": yesterday}
}))

if len(data) == 0:
    print("No posts found in last 24 hours.")
    exit()

df = pd.DataFrame(data)

# -------------------------------
# Only chosen topics
# -------------------------------
chosen_topics = [
    "AI", "Cricket", "Movies", "Education",
    "Technology", "Politics", "Health", "ClimateChange"
]

df = df[df["topic"].isin(chosen_topics)]

if len(df) == 0:
    print("No posts for selected topics.")
    exit()

# -------------------------------
# Sentiment distribution
# -------------------------------
sentiment_summary = (
    df["sentiment"].value_counts().to_dict()
)

# -------------------------------
# Top 5 topics (real ranking)
# -------------------------------
topic_summary = (
    df["topic"]
    .value_counts()
    .sort_values(ascending=False)
    .head(5)
    .to_dict()
)

# -------------------------------
# Final report
# -------------------------------
report = {
    "date": now.strftime("%Y-%m-%d"),
    "total_posts": len(df),
    "sentiment_summary": sentiment_summary,
    "top_topics": topic_summary,
    "generated_at": now
}

# -------------------------------
# Print report
# -------------------------------
print("\n📅 Daily Sentiment & Trend Report")
print("--------------------------------")
print(f"Date: {report['date']}")
print(f"Total Posts: {report['total_posts']}")

print("\nSentiment Distribution:")
for s, c in sentiment_summary.items():
    print(f"  {s}: {c}")

print("\nTop 5 Topics:")
for t, c in topic_summary.items():
    print(f"  {t}: {c}")

# -------------------------------
# Save report
# -------------------------------
report_collection.insert_one(report)
print("\n✅ Saved daily report to MongoDB (collection: daily_reports).")
