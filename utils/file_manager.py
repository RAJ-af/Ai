import re
import os
import zipfile
import io

def extract_code_blocks(text):
    # Matches [CODE_START]filename\ncode\n[CODE_END]
    pattern = r"\[CODE_START\](.*?)\n(.*?)\n\[CODE_END\]"
    matches = re.findall(pattern, text, re.DOTALL)
    return matches

def create_project_zip(agent_outputs, zip_filename="project.zip"):
    memory_zip = io.BytesIO()
    with zipfile.ZipFile(memory_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
        for output in agent_outputs:
            code_blocks = extract_code_blocks(output)
            for filename, code in code_blocks:
                # Sanitize filename
                filename = filename.strip()
                zf.writestr(filename, code.strip())

    memory_zip.seek(0)
    return memory_zip

def save_zip_to_disk(memory_zip, path="project.zip"):
    with open(path, "wb") as f:
        f.write(memory_zip.getbuffer())
    return os.path.abspath(path)
