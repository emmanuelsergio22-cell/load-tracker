import os
import json
import sqlite3
from datetime import date
from dotenv import load_dotenv
from anthropic import Anthropic
from vector_store import store_day, find_similar_days

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

def parse_day(training_summary, feel_text, food_text, past_days_context):
    prompt = f"""Training: {training_summary}
How the body feels: {feel_text}
What was eaten: {food_text}

Similar past days from history:
{past_days_context}

Return ONLY valid JSON, no markdown formatting, no explanation, with exactly these fields:
{{
  "soreness": <integer 1-10>,
  "fatigue": <integer 1-10>,
  "sleep_quality": "<short text, 'unknown' if not mentioned>",
  "nutrition_quality": "<short text assessing how adequate the food was for the training done>",
  "recommended_load": "<one of 'reduce', 'maintain', 'increase', followed by a one-sentence reason, referencing the past days above if they're relevant>"
}}"""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=250,
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

    combined_text = f"Training: {training_summary}. Feel: {feel_text}. Food: {food_text}."

    similar = find_similar_days(str(user_id), combined_text, n_results=3)
    past_docs = similar["documents"][0] if similar["documents"] else []
    past_days_context = "\n".join(past_docs) if past_docs else "No past days logged yet."

    parsed = parse_day(training_summary, feel_text, food_text, past_days_context)
    print("Claude's read on today:", parsed)
    print("Recommended load:", parsed["recommended_load"])

    cur.execute("""
        INSERT INTO logs (user_id, date, training_summary, feel_text, food_text, parsed_json, recommended_load)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user_id, date.today().isoformat(), training_summary, feel_text, food_text, json.dumps(parsed), parsed["recommended_load"]))

    log_id = cur.lastrowid
    conn.commit()
    conn.close()

    store_day(log_id, str(user_id), date.today().isoformat(), combined_text)

    print("Logged.")

if __name__ == "__main__":
    main()