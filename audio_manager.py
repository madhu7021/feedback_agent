import os
import sqlite3

from database import (
    DB_FILE,
    AUDIO_DIR,
    MAX_RECORDS
)


def save_audio(filename):

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO audios(filename) VALUES(?)",
        (filename,)
    )

    conn.commit()

    cur.execute("""
        SELECT id, filename
        FROM audios
        ORDER BY id DESC
    """)

    rows = cur.fetchall()

    if len(rows) > MAX_RECORDS:

        for row in rows[MAX_RECORDS:]:

            old_id = row[0]
            old_file = row[1]

            path = os.path.join(
                AUDIO_DIR,
                old_file
            )

            if os.path.exists(path):
                os.remove(path)

            cur.execute(
                "DELETE FROM audios WHERE id=?",
                (old_id,)
            )

    conn.commit()
    conn.close()


def get_audio_files():

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute("""
        SELECT filename
        FROM audios
        ORDER BY id DESC
    """)

    rows = cur.fetchall()

    conn.close()

    return [row[0] for row in rows]


def get_latest_audio():

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute("""
        SELECT filename
        FROM audios
        ORDER BY id DESC
        LIMIT 1
    """)

    row = cur.fetchone()

    conn.close()

    return row[0] if row else None