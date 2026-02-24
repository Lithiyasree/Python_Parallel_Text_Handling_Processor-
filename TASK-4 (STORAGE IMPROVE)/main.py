import csv
import sqlite3
import re
import time
from datetime import datetime

# START TIMER

overall_start = time.time()

# TEXT PREPROCESSING

def preprocess_text(text):
    return re.findall(r"\b\w+\b", text.lower())

# KEYWORD DICTIONARIES

quality_keywords = {
    "good": 1,
    "excellent": 2,
    "durable": 2,
    "cheap": -1,
    "poor": -2
}

price_keywords = {
    "worth": 2,
    "affordable": 2,
    "expensive": -1,
    "overpriced": -2
}

delivery_keywords = {
    "fast": 1,
    "ontime": 2,
    "late": -1,
    "delayed": -2
}

packaging_keywords = {
    "packed": 1,
    "damaged": -2,
    "broken": -2
}

performance_keywords = {
    "perfectly": 2,
    "smooth": 2,
    "slow": -1,
    "working": 1
}

# SCORE FUNCTION

def calculate_score(words, keyword_dict):
    score = 0
    for word in words:
        if word in keyword_dict:
            score += keyword_dict[word]
    return score


def process_review(text):
    words = preprocess_text(text)

    quality_score = calculate_score(words, quality_keywords)
    price_score = calculate_score(words, price_keywords)
    delivery_score = calculate_score(words, delivery_keywords)
    packaging_score = calculate_score(words, packaging_keywords)
    performance_score = calculate_score(words, performance_keywords)

    total_score = (
        quality_score + price_score + delivery_score +
        packaging_score + performance_score
    )

    if total_score > 0:
        sentiment = "Positive"
    elif total_score < 0:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return (
        text,
        "Yes" if quality_score > 0 else "No",
        "Yes" if price_score > 0 else "No",
        "Yes" if delivery_score > 0 else "No",
        "Yes" if packaging_score > 0 else "No",
        "Yes" if performance_score > 0 else "No",
        total_score,
        sentiment,
        timestamp
    )

# LOAD CSV (1 Million)

print("Loading CSV...")

with open(r"amazon-product-reviews.csv", "r", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    reviews = list(reader)[:1000000]   # Process up to 1M

print("Total Records Loaded:", len(reviews))


# DATABASE SETUP


conn = sqlite3.connect("C:\\Users\\rlith\\OneDrive\\Desktop\\INFOSYS SPRINGBOARD INTERN\\TASK\\TASK-4 (STORAGE IMPROVE)\\amazon-product-reviews.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT,
    quality_status TEXT,
    price_status TEXT,
    delivery_status TEXT,
    packaging_status TEXT,
    performance_status TEXT,
    total_score REAL,
    overall_sentiment TEXT,
    timestamp TEXT
)
""")

conn.commit()


# INSERT DATA (BULK INSERT)

print("Processing and Inserting Data...")

insert_start = time.time()

processed_data = []

for row in reviews:
    if "reviews.text" in row:
        result = process_review(row["reviews.text"])
        processed_data.append(result)

cursor.executemany("""
INSERT INTO results 
(text, quality_status, price_status, delivery_status, packaging_status,
 performance_status, total_score, overall_sentiment, timestamp)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""", processed_data)

conn.commit()

insert_end = time.time()
print("Insert Time:", round(insert_end - insert_start, 2), "seconds")


# QUERY BEFORE INDEX


query1_start = time.time()

cursor.execute("""
SELECT overall_sentiment, COUNT(*) 
FROM results 
GROUP BY overall_sentiment
""")
print("Query Result:", cursor.fetchall())

query1_end = time.time()
before_time = query1_end - query1_start

print("Query Time (Before Index):", round(before_time, 4), "seconds")


# ADD INDEXES (OPTIMIZATION)


print("Applying Indexes...")

cursor.execute("CREATE INDEX IF NOT EXISTS idx_sentiment ON results(overall_sentiment)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_total_score ON results(total_score)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON results(timestamp)")

conn.commit()


# QUERY AFTER INDEX


query2_start = time.time()

cursor.execute("""
SELECT overall_sentiment, COUNT(*) 
FROM results 
GROUP BY overall_sentiment
""")
print("Query Result:", cursor.fetchall())

query2_end = time.time()
after_time = query2_end - query2_start

print("Query Time (After Index):", round(after_time, 4), "seconds")


# PERFORMANCE COMPARISON


improvement = ((before_time - after_time) / before_time) * 100

print("\nPerformance Improvement:", round(improvement, 2), "%")

conn.close()

overall_end = time.time()
print("\nTotal Execution Time:", round(overall_end - overall_start, 2), "seconds")
print("Process Completed Successfully")