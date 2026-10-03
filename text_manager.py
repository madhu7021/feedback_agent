import sqlite3

from database import DB_FILE
from database import MAX_RECORDS


def save_prompt(prompt):

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO prompts(prompt) VALUES(?)",
        (prompt,)
    )

    cur.execute(f"""
        DELETE FROM prompts
        WHERE id NOT IN (
            SELECT id
            FROM prompts
            ORDER BY id DESC
            LIMIT {MAX_RECORDS}
        )
    """)

    conn.commit()
    conn.close()


def get_prompts():

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute("""
        SELECT prompt
        FROM prompts
        ORDER BY id DESC
    """)

    rows = cur.fetchall()

    conn.close()

    return [row[0] for row in rows]