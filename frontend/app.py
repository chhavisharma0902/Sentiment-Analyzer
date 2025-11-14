import streamlit as st
from pymongo import MongoClient
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# -------------------------------
# Page Config
# -------------------------------
st.set_page_config(
    page_title="Social Media Sentiment Dashboard",
    layout="wide"
)
st.title("📊 Real-Time Social Media Sentiment & Trend Dashboard")

# -------------------------------
# MongoDB Connection
# -------------------------------
client = MongoClient("mongodb+srv://Chhavi:Sharmacv%40123@sentimentanalyzer.elrkicj.mongodb.net/sentimentDB")
db = client["sentimentDB"]
posts_col = db["social_media_posts"]
reports_col = db["tweets"]

# -------------------------------
# Sidebar Filters
# -------------------------------
st.sidebar.header("🔍 Filters")

time_options = {
    "Last 1 Hour": 1,
    "Last 6 Hours": 6,
    "Last 12 Hours": 12,
    "Last 24 Hours": 24
}

time_window = st.sidebar.selectbox("Select Time Range", list(time_options.keys()))
time_delta = timedelta(hours=time_options[time_window])

# -------------------------------
# Fetch Data
# -------------------------------
start_time = datetime.now() - time_delta
posts = list(posts_col.find({"timestamp": {"$gte": start_time}}))

if not posts:
    st.warning("No posts found in the selected time range.")
    st.stop()

df = pd.DataFrame(posts)
df["timestamp"] = pd.to_datetime(df["timestamp"])

# -------------------------------
# SECTION 1: Sentiment Overview
# -------------------------------
st.subheader("📉 Sentiment Distribution")

sent_counts = df["sentiment"].value_counts().reset_index()
sent_counts.columns = ["Sentiment", "Count"]

col1, col2 = st.columns(2)

with col1:
    fig1 = px.pie(
        sent_counts,
        names="Sentiment",
        values="Count",
        title="Sentiment Proportion",
        color="Sentiment",
        color_discrete_map={
            "positive": "lightgreen",
            "negative": "red",
            "neutral": "yellow"
        }
    )
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = px.bar(
        sent_counts,
        x="Sentiment",
        y="Count",
        text="Count",
        title="Sentiment Count",
        color="Sentiment",
        color_discrete_map={
            "positive": "lightgreen",
            "negative": "red",
            "neutral": "yellow"
        }
    )
    st.plotly_chart(fig2, use_container_width=True)

# -------------------------------
# SECTION 2: Topic Trends
# -------------------------------
st.subheader("🔥 Top Trending Topics")

topic_counts = df["topic"].value_counts().reset_index()
topic_counts.columns = ["Topic", "Count"]

fig3 = px.bar(
    topic_counts.head(10),
    x="Topic",
    y="Count",
    title="Top 10 Trending Topics",
    color="Topic"
)
st.plotly_chart(fig3, use_container_width=True)

# -------------------------------
# SECTION 3: Time Series Trends
# -------------------------------
st.subheader("⏱️ Posts Over Time (Hourly Breakdown)")

df["time_slot"] = df["timestamp"].dt.floor("H")
time_trend = df.groupby(["time_slot", "sentiment"]).size().reset_index(name="count")

fig4 = px.line(
    time_trend,
    x="time_slot",
    y="count",
    color="sentiment",
    title="Posts Over Time (Sentiment-wise)"
)
st.plotly_chart(fig4, use_container_width=True)

# -------------------------------
# SECTION 4: Word Cloud
# -------------------------------
st.subheader("☁️ Word Cloud (Post Content)")

content_text = " ".join(df["content"].astype(str))

if content_text.strip():
    wc = WordCloud(
        width=900,
        height=400,
        background_color="white"
    ).generate(content_text)

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig)

# -------------------------------
# SECTION 5: Daily Summary
# -------------------------------
st.markdown("---")
st.header("🗂️ Daily Summary Reports")

summaries = list(reports_col.find().sort("date", -1).limit(5))

if summaries:
    for rpt in summaries:
        st.subheader(f"📅 Date: {rpt['date']}")
        st.write(f"**Total Posts:** {rpt['total_posts']}")
        st.write("**Sentiment Summary:**")
        st.json(rpt["sentiment_summary"])
        st.write("**Top Topics:**")
        st.json(rpt["top_topics"])
        st.markdown("---")
else:
    st.info("No daily reports found yet.")
