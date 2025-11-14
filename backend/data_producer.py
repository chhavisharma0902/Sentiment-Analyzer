from datetime import datetime, timedelta
from faker import Faker
import random
import time
import json
from kafka import KafkaProducer

fake = Faker()

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

topics = ["AI", "Cricket", "Movies", "Education", "Technology", "Politics", "Health", "ClimateChange"]

def generate_fake_tweets():
    try:
        while True:
            post = {
                "username": fake.user_name(),
                "content": fake.sentence(nb_words=10),
                "topic": random.choice(topics),
                "timestamp": datetime.utcnow().isoformat()  # FIXED
            }

            print("Producing:", post)
            producer.send("social_media_posts", post)
            time.sleep(2)

    except KeyboardInterrupt:
        print("\n🛑 Producer stopped manually.")
        producer.flush()
        producer.close()


if __name__ == "__main__":
    generate_fake_tweets()
