import streamlit as st
from pymongo import MongoClient
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os
load_dotenv()
mongo_uri = os.getenv("MONGO_URI")


# -------------------------------
# MongoDB Connection
# -------------------------------
mongo_uri = st.secrets["MONGO_URI"]
client = MongoClient(mongo_uri)
db = client["sentimentDB"]
posts_col = db["social_media_posts"]
reports_col = db["tweets"]

# -------------------------------
# Streamlit Page Config
# -------------------------------
st.set_page_config(page_title="Social Media Sentiment Dashboard", layout="wide")
st.title("📊 Real-Time Social Media Sentiment & Trend Dashboard")

# Sidebar filters
st.sidebar.header("🔍 Filter Options")
time_window = st.sidebar.selectbox(
    "Select Time Range",
    ["Last 1 Hour", "Last 6 Hours", "Last 12 Hours", "Last 24 Hours"],
    index=3
)
hours_map = {"Last 1 Hour":1, "Last 6 Hours":6, "Last 12 Hours":12, "Last 24 Hours":24}
time_delta = timedelta(hours=hours_map[time_window])

# -------------------------------
# Fetch Data from MongoDB
# -------------------------------
now = datetime.now()
start_time = now - time_delta
data = list(posts_col.find({"timestamp": {"$gte": start_time}}))

if not data:
    st.warning("No posts found in the selected time range.")
else:
    df = pd.DataFrame(data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # -------------------------------
    # Sentiment Distribution
    # -------------------------------
    st.subheader("💬 Sentiment Distribution")
    sentiment_counts = df['sentiment'].value_counts().reset_index()
    sentiment_counts.columns = ['Sentiment', 'Count']
    col1, col2 = st.columns(2)
    with col1:
        fig1 = px.pie(sentiment_counts, names='Sentiment', values='Count',
                      color='Sentiment',
                      color_discrete_map={'positive':'green','negative':'red','neutral':'gray'},
                      title="Sentiment Proportion")
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        fig2 = px.bar(sentiment_counts, x='Sentiment', y='Count', color='Sentiment',
                      title="Sentiment Count", text='Count',
                      color_discrete_map={'positive':'green','negative':'red','neutral':'gray'})
        st.plotly_chart(fig2, use_container_width=True)

    # -------------------------------
    # Topic Trends
    # -------------------------------
    st.subheader("🔥 Top Trending Topics")
    topic_counts = df['topic'].value_counts().reset_index()
    topic_counts.columns = ['Topic', 'Count']
    fig3 = px.bar(topic_counts.head(10), x='Topic', y='Count', color='Topic', title="Top 10 Topics")
    st.plotly_chart(fig3, use_container_width=True)

    # -------------------------------
    # Time Series (Volume over time)
    # -------------------------------
    st.subheader("⏱️ Posts Over Time")
    df['time_slot'] = df['timestamp'].dt.floor('H')
    time_trend = df.groupby(['time_slot','sentiment']).size().reset_index(name='count')
    fig4 = px.line(time_trend, x='time_slot', y='count', color='sentiment',
                   title="Posts Over Time by Sentiment")
    st.plotly_chart(fig4, use_container_width=True)

    # -------------------------------
    # Word Cloud (optional)
    # -------------------------------
    st.subheader("☁️ Word Cloud (Post Content)")
    text_data = " ".join(df["content"].astype(str))
    if text_data.strip():
        wc = WordCloud(width=800, height=400, background_color="white").generate(text_data)
        fig, ax = plt.subplots(figsize=(10,5))
        ax.imshow(wc, interpolation="bilinear")
        ax.axis("off")
        st.pyplot(fig)

# -------------------------------
# Daily Summary Section
# -------------------------------
st.markdown("---")
st.header("📅 Daily Summary Report")

daily_reports = list(reports_col.find().sort("date", -1).limit(5))
if daily_reports:
    for report in daily_reports:
        st.markdown(f"### Date: {report['date']}")
        st.write(f"**Total Posts:** {report['total_posts']}")
        st.write("**Sentiment Summary:**")
        st.json(report['sentiment_summary'])
        st.write("**Top Topics:**")
        st.json(report['top_topics'])
        st.markdown("---")
else:
    st.info("No daily reports found in the database yet.")
