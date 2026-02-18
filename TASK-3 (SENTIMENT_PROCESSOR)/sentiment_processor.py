import sqlite3
import pandas as pd
from datetime import datetime
import os
import sys

POSITIVE_WORDS = {"good","great","happy","love","excellent","awesome","best","amazing","fantastic","nice"}
NEGATIVE_WORDS = {"bad","worst","sad","hate","terrible","awful","poor","angry","disappointed","boring"}

DB_NAME = "sentiment_results.db"


def init_db():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("DROP TABLE IF EXISTS results")

        cursor.execute("""
        CREATE TABLE results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT,
            score INTEGER,
            sentiment TEXT,
            timestamp TEXT
        )
        """)

        conn.commit()
        conn.close()
        print("Database Ready")

    except sqlite3.Error as db_err:
        print("Database Initialization Error:", db_err)
        sys.exit(1)


def calculate_score(text):
    try:
        score = 0
        words = text.lower().split()

        for word in words:
            word = word.strip(".,!?;:\"'()[]{}")
            if word in POSITIVE_WORDS:
                score += 1
            elif word in NEGATIVE_WORDS:
                score -= 1

        return score

    except Exception as e:
        print("Error in scoring text:", e)
        return 0


def get_sentiment(score):
    if score > 0:
        return "Positive"
    elif score < 0:
        return "Negative"
    else:
        return "Neutral"


def process_data(texts):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        for text in texts:
            try:
                score = calculate_score(str(text))
                sentiment = get_sentiment(score)
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                cursor.execute("""
                INSERT INTO results (text, score, sentiment, timestamp)
                VALUES (?, ?, ?, ?)
                """, (text, score, sentiment, timestamp))

            except sqlite3.Error as insert_err:
                print("Error inserting row:", insert_err)

        conn.commit()
        conn.close()

    except sqlite3.Error as db_err:
        print("Database Processing Error:", db_err)
        sys.exit(1)


if __name__ == "__main__":

    try:
        dataset = input("Enter dataset file name (with .csv): ").strip()

        if not os.path.exists(dataset):
            raise FileNotFoundError("File does not exist.")

        try:
            df = pd.read_csv(dataset, encoding="latin-1")
        except pd.errors.EmptyDataError:
            print("CSV file is empty.")
            sys.exit(1)
        except pd.errors.ParserError:
            print("Error parsing CSV file.")
            sys.exit(1)

        print("\nAvailable Columns:\n")
        for i, col in enumerate(df.columns):
            print(f"{i} → {col}")

        try:
            choice = int(input("\nEnter column number for review text: "))
        except ValueError:
            print("Please enter a valid numeric column index.")
            sys.exit(1)

        if choice < 0 or choice >= len(df.columns):
            raise IndexError("Selected column number is out of range.")

        text_col = df.columns[choice]
        print("Selected Column:", text_col)

        texts = df[text_col].dropna()

        init_db()
        process_data(texts[:1000])  # Limit for testing

        print("Processing Completed Successfully")

    except FileNotFoundError as fnf:
        print("File Error:", fnf)

    except IndexError as idx_err:
        print("Column Selection Error:", idx_err)

    except Exception as e:
        print("Unexpected Error:", e)
