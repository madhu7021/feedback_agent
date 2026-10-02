import os
import re
import sqlite3
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs

DB_FILE = "prompts.db"
AUDIO_DIR = "audio_records"

# ==================================================
# Database
# ==================================================
def init_db():

    os.makedirs(AUDIO_DIR, exist_ok=True)

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS prompts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS audios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# ==================================================
# Prompt Functions
# ==================================================
def save_prompt(prompt):

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO prompts(prompt) VALUES(?)",
        (prompt,)
    )

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


# ==================================================
# Audio Functions
# ==================================================
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

    if len(rows) > 10:

        for row in rows[10:]:

            old_id = row[0]
            old_file = row[1]

            full_path = os.path.join(
                AUDIO_DIR,
                old_file
            )

            if os.path.exists(full_path):
                os.remove(full_path)

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

    if row:
        return row[0]

    return None


# ==================================================
# HTTP Handler
# ==================================================
class PromptHandler(BaseHTTPRequestHandler):

    def render_page(
            self,
            message="",
            prompts=None,
            audio_files=None):

        if prompts is None:
            prompts = []
        
        if audio_files is None:
            audio_files = []
        
        prompt_html = ""

        audio_html = ""

        if audio_files:

            audio_html = """
            <h3>Saved Audio Files (Latest 10)</h3>
            <ul>
            """

            for audio in audio_files:

                audio_html += f"""
                <li>
                    /audio/{audio}
                        {audio}
                    </a>
                </li>
                """

            audio_html += "</ul>"
    
        if prompts:

            prompt_html = """
            <h3>Saved Prompts (Latest 10)</h3>
            <ul>
            """

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
    background:#f5f5f5;
    padding:30px;
}}

.container {{
    width:800px;
    background:white;
    padding:20px;
    border-radius:10px;
    box-shadow:0 0 10px rgba(0,0,0,.2);
}}

textarea {{
    width:100%;
    height:100px;
}}

button {{
    padding:10px 20px;
    margin-top:10px;
    margin-right:10px;
}}

.message {{
    color:green;
    margin-top:15px;
    font-weight:bold;
}}

</style>

<script>

let mediaRecorder;
let recordedChunks = [];
let isRecording = false;

function clearText()
{{
    document.getElementById("prompt").value="";
}}

async function startRecording()
{{
    if(isRecording)
    {{
        alert("Recording already in progress");
        return;
    }}

    const stream =
        await navigator.mediaDevices.getUserMedia(
        {{
            audio:true
        }}
    );

    mediaRecorder =
        new MediaRecorder(
            stream,
            {{
                mimeType:'audio/webm'
            }}
        );

    recordedChunks = [];

    mediaRecorder.ondataavailable =
        function(e)
        {{
            if(e.data.size > 0)
            {{
                recordedChunks.push(e.data);
            }}
        }}

    mediaRecorder.start();

    isRecording = true;

    document.getElementById(
        "record_status"
    ).innerHTML =
        "🔴 Recording...";
}}

async function stopRecording()
{{
    if(!isRecording)
    {{
        alert("No active recording");
        return;
    }}

    mediaRecorder.stop();

    mediaRecorder.onstop =
    async function()
    {{
        const blob =
            new Blob(
                recordedChunks,
                {{
                    type:'audio/webm'
                }}
            );

        const formData =
            new FormData();

        const filename =
            "audio_" +
            Date.now() +
            ".webm";

        formData.append(
            "audio",
            blob,
            filename
        );

        await fetch(
            "/upload_audio",
            {{
                method:"POST",
                body:formData
            }}
        );

        document.getElementById(
            "record_status"
        ).innerHTML =
            "✅ Recording Saved";

        alert("Audio Saved");
    }}

    isRecording = false;
}}

function playLatestAudio()
{{
    let player =
        document.getElementById(
            "audioPlayer"
        );

    player.src = "/latest_audio";

    player.load();

    player.play();
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

<button type="submit"
        name="action"
        value="save">
Submit
</button>

<button type="submit"
        name="action"
        value="show">
Show Prompts
</button>

<button type="button"
        onclick="clearText()">
Clear
</button>

<br><br>

<button type="button"
        onclick="startRecording()">
Audio_Start_Record
</button>

<button type="button"
        onclick="stopRecording()">
Audio_Stop_Record
</button>

<button type="button"
        onclick="playLatestAudio()">
Audio_Play
</button>

<button type="submit"
        name="action"
        value="show_audio">
Show Audio
</button>

</form>

<div id="record_status"></div>

<br>

<audio
id="audioPlayer"
controls
style="display:none;width:100%;">
</audio>

<div class="message">
{message}
</div>

{prompt_html}

{audio_html}

</div>

</body>
</html>
"""

        self.send_response(200)
        self.send_header(
            "Content-Type",
            "text/html"
        )
        self.end_headers()

        self.wfile.write(
            html.encode("utf-8")
        )

    # ------------------------------------------------

    def do_GET(self):

        if self.path == "/latest_audio":
            
            print("Latest requested")
            latest = get_latest_audio()
            print("Latest file:", latest)
            
            if latest:

                file_path = os.path.join(
                    AUDIO_DIR,
                    latest
                )
                print("Full path:", file_path)
                
                if os.path.exists(file_path):
                    
                    print("Exists:", os.path.exists(file_path))
                    self.send_response(200)
                    self.send_header(
                        "Content-Type",
                        "audio/webm"
                    )
                    self.end_headers()

                    with open(
                        file_path,
                        "rb"
                    ) as f:
                        self.wfile.write(
                            f.read()
                        )

                    return

        elif self.path.startswith("/audio/"):

            filename = self.path.split("/")[-1]

            file_path = os.path.join(
                AUDIO_DIR,
                filename
            )

            if os.path.exists(file_path):

                self.send_response(200)
                self.send_header(
                    "Content-Type",
                    "audio/webm"
                )
                self.end_headers()

                with open(
                    file_path,
                    "rb"
                ) as f:
                    self.wfile.write(
                        f.read()
                    )

                return

        self.render_page()

    # ------------------------------------------------

    def do_POST(self):

        #
        # Audio Upload
        #
        if self.path == "/upload_audio":
            
            content_length = int(
                self.headers['Content-Length']
            )

            data = self.rfile.read(content_length)

            boundary = self.headers[
                'Content-Type'
            ].split("boundary=")[1].encode()

            parts = data.split(
                b'--' + boundary
            )

            for part in parts:

                if b'filename="' in part:

                    match = re.search(
                        rb'filename="([^"]+)"',
                        part
                    )

                    if not match:
                        continue

                    filename = match.group(
                        1
                    ).decode()

                    header_end = part.find(
                        b'\r\n\r\n'
                    )

                    if header_end == -1:
                        continue

                    file_data = part[
                        header_end + 4:
                    ]

                    file_data = file_data.rstrip(
                        b'\r\n'
                    )

                    save_path = os.path.join(
                        AUDIO_DIR,
                        filename
                    )

                    with open(
                        save_path,
                        "wb"
                    ) as f:
                        f.write(file_data)

                    save_audio(filename)

                    break
            
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
            return

        #
        # Form handling
        #
        content_length = int(
            self.headers["Content-Length"]
        )

        post_data = self.rfile.read(
            content_length
        ).decode("utf-8")

        form = parse_qs(post_data)

        action = form.get(
            "action",
            [""]
        )[0]

        prompt = form.get(
            "prompt",
            [""]
        )[0].strip()

        if action == "save":

            if prompt:

                save_prompt(prompt)

                self.render_page(
                    "Prompt saved successfully."
                )

            else:

                self.render_page(
                    "Prompt cannot be empty."
                )

        elif action == "show":

            prompts = get_prompts()

            self.render_page(
                prompts=prompts
            )
        
        elif action == "show_audio":

            print("Showing audio")
            audio_files = get_audio_files()
            
            self.render_page(
                audio_files=audio_files
            )
        else:

            self.render_page()


# ==================================================
# Main
# ==================================================
if __name__ == "__main__":

    init_db()

    server = HTTPServer(
        ("0.0.0.0", 8000),
        PromptHandler
    )

    print("Server Started")
    print("Open http://localhost:8000")

    server.serve_forever()