#  Real-Time Sentiment Analyzer

🚀 **Live Dashboard:**  
https://sentiment-analyzer-pqgemux9tdce7xbmv4ie4w.streamlit.app/


A real-time sentiment analysis system that uses **Faker-generated social media posts** to simulate live data streams.  
The project integrates **Kafka**, **BERT-based NLP**, **MongoDB**, **Streamlit**, and **Airflow** to provide insights, analytics, and automated daily reports.

---

##  Features

- 🔄 **Real-time data generation** using the Faker library  
- 🧠 **Transformer-based sentiment analysis** (BERT model for Twitter data)  
- 📦 **Data pipeline with Kafka** for streaming  
- 🗃️ **MongoDB** for storing processed posts and daily summaries  
- 📊 **Streamlit Dashboard** for live visualization of sentiment trends  
- 🕒 **Airflow DAGs** for automated daily trend reports  

---

##  Tech Stack

| Component | Technology |
|------------|-------------|
| Data Source | Faker Library |
| Stream Processing | Apache Kafka |
| NLP Model | BERT (Twitter RoBERTa) |
| Database | MongoDB |
| Visualization | Streamlit |
| Scheduler | Apache Airflow |
| Language | Python 3 |

---

##  How It Works

1. **Fake Post Generation:** Faker library simulates social media posts in real time.  
2. **Kafka Streaming:** Posts are streamed through Apache Kafka.  
3. **Sentiment Analysis:** Each post is analyzed using a BERT model.  
4. **Storage:** Results are stored in MongoDB.  
5. **Visualization:** Streamlit dashboard displays real-time trends.  
6. **Automation:** Airflow DAG generates daily sentiment trend reports.

---

## 🖥️ Run Locally

```bash
# 1️⃣ Clone this repository
git clone https://github.com/<your-username>/sentiment-analyzer.git
cd sentiment-analyzer

# 2️⃣ Set up virtual environment
python -m venv venv
venv\Scripts\activate  # (Windows)
source venv/bin/activate  # (Linux/Mac)

# 3️⃣ Install dependencies
pip install -r requirements.txt
python -m textblob.download_corpora

# 4️⃣ Start Kafka, MongoDB, and run producer & consumer
python backend/data_producer.py
python backend/data_consumer.py

# 5️⃣ View dashboard
streamlit run dashboard/dashboard.py

