import os
import re
import sqlite3
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs

from database import (
    init_db,
    AUDIO_DIR,
    IMAGE_DIR
)

from text_manager import (
    save_prompt,
    get_prompts
)

from audio_manager import (
    save_audio,
    get_audio_files,
    get_latest_audio
)

from image_manager import (
    is_valid_image,
    save_image,
    get_image_files,
    get_latest_image
)

from html_handler import (
    build_page
)

from ui_builder import (
    build_prompt_html,
    build_audio_html,
    build_latest_image_html,
    build_image_html
)

#
# ==================================================
# HTTP Handler
# ==================================================
class PromptHandler(BaseHTTPRequestHandler):

    def render_page(
            self,
            message="",
            prompts=None,
            audio_files=None,
            image_files=None,
            latest_image=None):

        if prompts is None:
            prompts = []
        
        if audio_files is None:
            audio_files = []
            
        if image_files is None:
            image_files = []
        
        prompt_html = build_prompt_html(
            prompts
        )

        audio_html = build_audio_html(
            audio_files
        )

        latest_image_html = build_latest_image_html(
            latest_image
        )

        image_html = build_image_html(
            image_files
        )
        
        html = build_page(
            message,
            prompt_html,
            audio_html,
            latest_image_html,
            image_html
        )
        
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

        elif self.path.startswith("/image/"):

            filename = self.path.split("/")[-1]

            image_path = os.path.join(
                IMAGE_DIR,
                filename
            )

            if os.path.exists(image_path):

                ext = filename.lower()

                if ext.endswith(".png"):
                    mime = "image/png"

                elif ext.endswith(".gif"):
                    mime = "image/gif"

                elif ext.endswith(".webp"):
                    mime = "image/webp"

                else:
                    mime = "image/jpeg"

                self.send_response(200)

                self.send_header(
                    "Content-Type",
                    mime
                )

                self.end_headers()

                with open(
                    image_path,
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
        # Image Upload
        #
        if self.path == "/upload_image":

            print("IMAGE UPLOAD REQUEST")

            content_length = int(
                self.headers["Content-Length"]
            )

            data = self.rfile.read(
                content_length
            )

            boundary = self.headers[
                "Content-Type"
            ].split("boundary=")[1].encode()

            parts = data.split(
                b"--" + boundary
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

                    print(
                        "Image filename:",
                        filename
                    )

                    if not is_valid_image(
                        filename
                    ):
                        self.send_response(400)
                        self.end_headers()
                        self.wfile.write(
                            b"Invalid Image Type"
                        )
                        return

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
                        IMAGE_DIR,
                        filename
                    )

                    print(
                        "Saving to:",
                        save_path
                    )

                    with open(
                        save_path,
                        "wb"
                    ) as f:

                        f.write(file_data)

                    save_image(filename)

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
        
        elif action == "show_image":

            print("Showing image")
            self.render_page(
                latest_image=get_latest_image()
            )
            
        elif action == "list_image":
            
            print("Listing image")
            self.render_page(
                image_files=get_image_files()
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