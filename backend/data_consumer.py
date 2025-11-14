from kafka import KafkaConsumer
import json
from pymongo import MongoClient
from datetime import datetime
import sys
import os

# -------------------------------
# Connect to MongoDB
# -------------------------------
mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
mongo_client = MongoClient(mongo_uri)
db = mongo_client["sentimentDB"]
collection = db["social_media_posts"]

# -------------------------------
# Connect to Kafka
# -------------------------------
kafka_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9093').split(',')
consumer = KafkaConsumer(
    'social_media_posts',
    bootstrap_servers=kafka_servers,
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='sentiment-group',
    value_deserializer=lambda v: json.loads(v.decode('utf-8'))
)

print("📡 Listening for new social media posts...")

# -------------------------------
# Sentiment analysis function (library-based)
# -------------------------------
def get_sentiment(text: str) -> str:
    try:
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
        analyzer = SentimentIntensityAnalyzer()
        scores = analyzer.polarity_scores(str(text))
        comp = scores.get('compound', 0.0)
        if comp > 0.05:
            return "positive"
        elif comp < -0.05:
            return "negative"
        else:
            return "neutral"
    except Exception:
        try:
            from textblob import TextBlob
            polarity = TextBlob(str(text)).sentiment.polarity
            if polarity > 0.05:
                return "positive"
            elif polarity < -0.05:
                return "negative"
            else:
                return "neutral"
        except Exception:
            print("\n[error] No supported sentiment library available.")
            print("  pip install vaderSentiment")
            print("  pip install textblob nltk scipy")
            print("  python -m textblob.download_corpora")
            sys.exit(1)

# -------------------------------
# Consume messages and store in MongoDB
# -------------------------------
try:
    for message in consumer:
        post = message.value

        # --- Sentiment ---
        sentiment = get_sentiment(post["content"])
        print("Git sentiment for new social media post...")
        post["sentiment"] = sentiment

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