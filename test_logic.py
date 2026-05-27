import sys
import os
sys.path.append('/app')
from utils.file_manager import extract_code_blocks, create_project_zip
import io

def test_extraction():
    text = """
    Hello, here is the code:
    [CODE_START]app.py
    print('hello world')
    [CODE_END]
    And another one:
    [CODE_START]styles.css
    body { color: red; }
    [CODE_END]
    """
    blocks = extract_code_blocks(text)
    print(f"Extracted blocks: {blocks}")
    assert len(blocks) == 2
    assert blocks[0][0].strip() == "app.py"
    assert "print('hello world')" in blocks[0][1]

def test_zipping():
    text = "[CODE_START]test.txt\ncontent\n[CODE_END]"
    zip_buf = create_project_zip([text])
    import zipfile
    with zipfile.ZipFile(zip_buf, 'r') as zf:
        files = zf.namelist()
        print(f"Zip files: {files}")
        assert "test.txt" in files
        with zf.open("test.txt") as f:
            assert f.read().decode().strip() == "content"

if __name__ == "__main__":
    test_extraction()
    test_zipping()
    print("Tests passed!")
