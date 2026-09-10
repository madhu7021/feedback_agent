import sqlite3
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs

DB_FILE = "prompts.db"


# -----------------------------
# Database Functions
# -----------------------------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS prompts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def save_prompt(prompt):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO prompts(prompt) VALUES (?)",
        (prompt,)
    )

    # Keep only latest 10 records
    cur.execute("""
        DELETE FROM prompts
        WHERE id NOT IN (
            SELECT id
            FROM prompts
            ORDER BY id DESC
            LIMIT 10
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


# -----------------------------
# Web UI
# -----------------------------
class PromptHandler(BaseHTTPRequestHandler):

    def render_page(self, message="", prompts=None):
        if prompts is None:
            prompts = []

        prompt_html = ""

        if prompts:
            prompt_html = "<h3>Saved Prompts (Latest 10)</h3><ul>"
            for p in prompts:
                prompt_html += f"<li>{p}</li>"
            prompt_html += "</ul>"

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Prompt Manager</title>

            <style>
                body {{
                    font-family: Arial, sans-serif;
                    padding: 30px;
                    background: #f5f5f5;
                }}

                .container {{
                    background: white;
                    padding: 20px;
                    width: 700px;
                    border-radius: 10px;
                    box-shadow: 0 0 10px rgba(0,0,0,0.1);
                }}

                textarea {{
                    width: 100%;
                    height: 100px;
                    font-size: 16px;
                }}

                button {{
                    padding: 10px 20px;
                    margin-right: 10px;
                    margin-top: 10px;
                    cursor: pointer;
                }}

                .message {{
                    color: green;
                    font-weight: bold;
                    margin-top: 10px;
                }}
            </style>

            <script>
                function clearText() {{
                    document.getElementById("prompt").value = "";
                }}
            </script>
        </head>

        <body>

        <div class="container">

            <h2>Prompt Storage Application</h2>

            <form method="POST">

                <textarea
                    id="prompt"
                    name="prompt"
                    placeholder="Enter your prompt here..."
                ></textarea>

                <br>

                <button type="submit" name="action" value="save">
                    Submit
                </button>

                <button type="submit" name="action" value="show">
                    Show Prompts
                </button>

                <button type="button" onclick="clearText()">
                    Clear
                </button>

            </form>

            <div class="message">
                {message}
            </div>

            {prompt_html}

        </div>

        </body>
        </html>
        """

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def do_GET(self):
        self.render_page()

    def do_POST(self):
        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length).decode("utf-8")

        form = parse_qs(post_data)

        action = form.get("action", [""])[0]
        prompt = form.get("prompt", [""])[0].strip()

        if action == "save":
            if prompt:
                save_prompt(prompt)
                self.render_page(
                    message="Prompt saved successfully."
                )
            else:
                self.render_page(
                    message="Prompt cannot be empty."
                )

        elif action == "show":
            prompts = get_prompts()
            self.render_page(prompts=prompts)

        else:
            self.render_page()


# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":
    init_db()

    server = HTTPServer(("0.0.0.0", 8000), PromptHandler)

    print("Server started")
    print("Open: http://localhost:8000")

    server.serve_forever()