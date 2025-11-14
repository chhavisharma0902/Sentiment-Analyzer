from kafka import KafkaConsumer
from textblob import TextBlob
import json
from pymongo import MongoClient
from datetime import datetime

# -------------------------------
# Connect to MongoDB
# -------------------------------
mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client["sentimentDB"]
collection = db["social_media_posts"]

# -------------------------------
# Connect to Kafka
# -------------------------------
consumer = KafkaConsumer(
    'social_media_posts',
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='latest',
    enable_auto_commit=True,
    group_id='sentiment-group',
    value_deserializer=lambda v: json.loads(v.decode('utf-8'))
)

print("📡 Listening for new social media posts...")


def get_sentiment(text):
    polarity = TextBlob(text).sentiment.polarity
    if polarity > 0.05:
        return "positive"
    elif polarity < -0.05:
        return "negative"
    return "neutral"


def normalize_topic(topic):
    if not topic:
        return "General"
    
    t = topic.replace(" ", "").replace("-", "").lower()
    if t == "climatechange":
        return "ClimateChange"
    return topic


try:
    for message in consumer:
        post = message.value

        # Sentiment
        post["sentiment"] = get_sentiment(post["content"])

        # Normalize topic
        post["topic"] = normalize_topic(post.get("topic", "General"))

        # Handle timestamp
        raw_ts = post.get("timestamp")
        try:
            post["timestamp"] = datetime.fromisoformat(raw_ts)
        except Exception as e:
            print("⚠️ Timestamp parse failed:", e, " | Using now().")
            post["timestamp"] = datetime.now()

        # Insert into DB
        collection.insert_one(post)

        print(
            f"✅ Stored post by @{post['username']} | "
            f"Sentiment: {post['sentiment']} | "
            f"Topic: {post['topic']} | "
            f"Timestamp: {post['timestamp']}"
        )

except KeyboardInterrupt:
    print("🛑 Consumer stopped manually.")
