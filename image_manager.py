import os
import sqlite3

from database import (
    DB_FILE,
    IMAGE_DIR,
    MAX_RECORDS
)

ALLOWED_IMAGE_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp"
}


def is_valid_image(filename):

    ext = os.path.splitext(
        filename
    )[1].lower()

    return (
        ext in
        ALLOWED_IMAGE_EXTENSIONS
    )


def save_image(filename):

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO images(filename) VALUES(?)",
        (filename,)
    )

    conn.commit()

    cur.execute("""
        SELECT id, filename
        FROM images
        ORDER BY id DESC
    """)

    rows = cur.fetchall()

    if len(rows) > MAX_RECORDS:

        for row in rows[MAX_RECORDS:]:

            old_id = row[0]
            old_file = row[1]

            path = os.path.join(
                IMAGE_DIR,
                old_file
            )

            if os.path.exists(path):
                os.remove(path)

            cur.execute(
                "DELETE FROM images WHERE id=?",
                (old_id,)
            )

    conn.commit()
    conn.close()


def get_image_files():

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute("""
        SELECT filename
        FROM images
        ORDER BY id DESC
    """)

    rows = cur.fetchall()

    conn.close()

    return [row[0] for row in rows]


def get_latest_image():

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute("""
        SELECT filename
        FROM images
        ORDER BY id DESC
        LIMIT 1
    """)

    row = cur.fetchone()

    conn.close()

    return row[0] if row else None