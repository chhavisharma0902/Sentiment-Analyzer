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

# -------------------------------
# Sentiment analysis function
# -------------------------------
def get_sentiment(text):
    polarity = TextBlob(text).sentiment.polarity
    if polarity > 0.05:
        return "positive"
    elif polarity < -0.05:
        return "negative"
    else:
        return "neutral"

# -------------------------------
# Consume messages and store in MongoDB
# -------------------------------
try:
    for message in consumer:
        post = message.value

        # --- Sentiment ---
        sentiment = get_sentiment(post["content"])
        post["sentiment"] = sentiment

        # --- Keep the topic from producer ---
        # --- Keep the topic from producer ---
        # Keep topic from producer but normalize
        topic = post.get("topic", "General")
        if topic.lower() == "climatechange":
            topic = "ClimateChange"  # normalize to match chosen_topics
        post["topic"] = topic

        # --- Timestamp ---
        post["timestamp"] = datetime.now()

        # --- Store to MongoDB ---
        collection.insert_one(post)
        print(f"✅ Stored post by @{post['username']} | Sentiment: {sentiment} | Topic: {post['topic']} | Timestamp: {post['timestamp']}")

except KeyboardInterrupt:
    print("🛑 Consumer stopped manually.")
