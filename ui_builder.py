def build_prompt_html(prompts):

    if not prompts:
        return ""

    html = """
    <h3>Saved Prompts (Latest 10)</h3>
    <ul>
    """

    for prompt in prompts:

        html += f"<li>{prompt}</li>"

    html += "</ul>"

    return html

def build_audio_html(audio_files):

    if not audio_files:
        return ""

    html = """
    <h3>Saved Audio Files (Latest 10)</h3>
    <ul>
    """

    for audio in audio_files:

        html += f"""
        <li>
            /audio/{audio}
                {audio}
            </a>
        </li>
        """

    html += "</ul>"

    return html
	
def build_latest_image_html(latest_image):

    if not latest_image:
        return ""

    return f"""
    <h3>Latest Uploaded Image</h3>

    <img
        src="/image/{latest_image}"
        width="300">
    """

def build_image_html(image_files):

    if not image_files:
        return ""

    html = """
    <h3>Images (Latest 10)</h3>

    <div style="
        display:flex;
        flex-wrap:wrap;
        gap:20px;
    ">
    """

    for image in image_files:

        html += f"""
        <div style="
            width:220px;
            text-align:center;
            border:1px solid #ddd;
            border-radius:8px;
            padding:10px;
            background:#fafafa;
        ">

        /image/{image}

        <img
                   </a>

        <br><br>

        <div style="
            font-size:12px;
            word-wrap:break-word;
            overflow-wrap:break-word;
        ">
            {image}
        </div>

        </div>
        """

    html += "</div>"

    return html