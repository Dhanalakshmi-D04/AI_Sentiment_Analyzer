import sqlite3
from flask import Flask, request, render_template, jsonify
from datetime import datetime
from transformers import pipeline

# Sentiment Analyzer
sentiment_pipeline = pipeline("sentiment-analysis")

def analyze_sentiment(text):
    result = sentiment_pipeline(text)[0]
    return result['label'], result['score']

# SQLite DB Setup
def get_db_connection():
    conn = sqlite3.connect('sentimentDB.db')  # SQLite file
    conn.row_factory = sqlite3.Row
    return conn

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        text = request.form['review']
        label, score = analyze_sentiment(text)

        # Save locally or just skip saving for now
        # For example, print it to console instead
        print({
            "text": text,
            "sentiment": label,
            "confidence": score,
            "timestamp": datetime.now()
        })

        return render_template('index.html', sentiment=label, score=round(score, 2))

    return render_template('index.html')



@app.route('/report')
def report():
    conn = get_db_connection()
    sentiments = conn.execute('SELECT sentiment FROM reviews').fetchall()
    conn.close()

    positive = sum(1 for s in sentiments if s['sentiment'] == 'POSITIVE')
    negative = sum(1 for s in sentiments if s['sentiment'] == 'NEGATIVE')
    neutral = sum(1 for s in sentiments if s['sentiment'] == 'NEUTRAL')

    return jsonify({
        "positive": positive,
        "negative": negative,
        "neutral": neutral
    })

if __name__ == '__main__':
    # Create a new SQLite table if it doesn't exist
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS reviews (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        text TEXT,
                        sentiment TEXT,
                        confidence REAL,
                        timestamp TEXT)''')
    conn.close()
    app.run(debug=True)
