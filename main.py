import os
import json
import sqlite3
from datetime import date
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic()

DB_PATH = "load_tracker.db"

def get_or_create_user(cur, name):
    cur.execute("SELECT id FROM users WHERE name = ?", (name,))
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute("INSERT INTO users (name) VALUES (?)", (name,))
    return cur.lastrowid

def parse_day(training_summary, feel_text, food_text):
    prompt = f"""Training: {training_summary}
How the body feels: {feel_text}
What was eaten: {food_text}

Return ONLY valid JSON, no markdown formatting, no explanation, with exactly these fields:
{{
  "soreness": <integer 1-10>,
  "fatigue": <integer 1-10>,
  "sleep_quality": "<short text, 'unknown' if not mentioned>",
  "nutrition_quality": "<short text assessing how adequate the food was for the training done>",
  "recommended_load": "<one of 'reduce', 'maintain', 'increase', followed by a one-sentence reason>"
}}"""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.content[0].text.strip()

    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.startswith("json"):
            raw = raw[4:].strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        print("Could not parse Claude's response as JSON:")
        print(raw)
        raise

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    user_id = get_or_create_user(cur, "sergio")

    print("Log today's session:")
    training_summary = input("Training done: ")
    feel_text = input("How your body feels: ")
    food_text = input("What you ate today: ")

    parsed = parse_day(training_summary, feel_text, food_text)
    print("Claude's read on today:", parsed)
    print("Recommended load:", parsed["recommended_load"])

    cur.execute("""
    INSERT INTO logs (user_id, date, training_summary, feel_text, food_text, parsed_json, recommended_load)
    VALUES (?, ?, ?, ?, ?, ?, ?)
""", (user_id, date.today().isoformat(), training_summary, feel_text, food_text, json.dumps(parsed), parsed["recommended_load"]))

    conn.commit()
    conn.close()
    print("Logged.")

if __name__ == "__main__":
    main()