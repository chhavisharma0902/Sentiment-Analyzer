from faker import Faker
import random
import time
import json
import os
import sys
from kafka import KafkaProducer

fake = Faker()

# Available topics
TOPICS = ["AI", "Cricket", "Movies", "Education", "Technology", "Politics", "Health", "ClimateChange"]

def create_producer():
    """Create and return a KafkaProducer"""
    servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9093').split(',')
    try:
        print(f"Connecting to Kafka at {servers}...")
        return KafkaProducer(
            bootstrap_servers=servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            request_timeout_ms=10000,
            api_version_auto_timeout_ms=5000
        )
    except TypeError:
        print("⚠ KafkaProducer init failed — retrying with manual api_version")
        api_version_str = os.getenv('KAFKA_API_VERSION', None)
        if api_version_str:
            try:
                api_version = tuple(int(x) for x in api_version_str.split(','))
                print(f"Retrying with api_version={api_version} ...")
                return KafkaProducer(
                    bootstrap_servers=servers,
                    api_version=api_version,
                    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                    request_timeout_ms=10000
                )
            except Exception as e:
                print(f"Retry failed: {e}")
                sys.exit(1)

        print("❌ Could not initialize KafkaProducer.")
        print(f"➡ Make sure Kafka is running and reachable at: {servers}")
        sys.exit(1)

    except Exception as e:
        print(f"❌ Producer initialization error: {e}")
        print(f"➡ Ensure Kafka is reachable at: {servers}")
        sys.exit(1)


def stream_fake_posts(producer):
    """Continuously generate and publish fake tweets to Kafka"""
    count = 0
    try:
        print("✅ Connected to Kafka. Starting to produce messages...")
        while True:
            post = {
                "username": fake.user_name(),
                "content": fake.sentence(nb_words=10),
                "topic": random.choice(TOPICS),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            print(f"📤 Producing → {post}")
            future = producer.send("social_media_posts", value=post)
            # Use get() to retrieve result synchronously and handle errors
            try:
                record_metadata = future.get(timeout=10)
                print(f"  ✅ Confirmed: partition {record_metadata.partition}, offset {record_metadata.offset}")
                count += 1
            except Exception as e:
                print(f"  ❌ Send failed: {e}")
            time.sleep(7)

    except KeyboardInterrupt:
        print("\n🛑 Producer stopped manually.")
    except Exception as e:
        print(f"❌ Error during production: {e}")
        sys.exit(1)
    finally:
        try:
            producer.flush()
            producer.close()
            print(f"✅ Produced {count} messages and closed producer.")
        except Exception as e:
            print(f"⚠ Error closing producer: {e}")


if __name__ == "__main__":
    producer = create_producer()
    stream_fake_posts(producer)
    stream_fake_posts(producer)
