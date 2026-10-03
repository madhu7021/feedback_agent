def build_page(
message,
prompt_html,
audio_html,
latest_image_html,
image_html): 
       return f"""
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

        async function uploadImage()
        {{
            const file = document.getElementById(
                    "imageFile"
                ).files[0];

            if(!file)
                return;

            const formData =
                new FormData();

            formData.append(
                "image",
                file,
                file.name
            );

            const response = await fetch(
                    "/upload_image",
                    {{
                        method: "POST",
                        body: formData
                    }}
                );

            if(response.ok)
            {{
                alert("Image Uploaded");
            }}
            else
            {{
                alert("Upload Failed");
            }}
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

        <input
            type="file"
            id="imageFile"
            accept="image/png,image/jpeg,image/gif,image/webp"
            style="display:none"
            onchange="uploadImage()">

        <br>

        <button type="submit"
                name="action"
                value="save">
        Save Prompt
        </button>

        <button type="submit"
                name="action"
                value="show">
        Show Prompt
        </button>

        <button type="button"
                onclick="clearText()">
        Clear Prompt
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

        <br><br>

        <button
                type="button"
                onclick="document.getElementById('imageFile').click();">
        Image_Upload
        </button>

        <button
                type="submit"
                name="action"
                value="show_image">
        Image_Show
        </button>

        <button
            type="submit"
            name="action"
            value="list_image">
        Image_List
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

        {latest_image_html}

        {image_html}

        </div>

        </body>
        </html>
        """