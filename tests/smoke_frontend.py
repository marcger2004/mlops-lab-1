"""Run inside the frontend container against the real inference service.

Copy this file and a sample image to /tmp, then run:
    python /tmp/smoke_frontend.py /tmp/food11-sample.jpg
"""
import sys

from streamlit.testing.v1 import AppTest

sample = sys.argv[1]
script = f'''
from io import BytesIO
from pathlib import Path
from unittest.mock import patch
import runpy

uploaded = BytesIO(Path({sample!r}).read_bytes())
uploaded.name = "sample.jpg"
uploaded.type = "image/jpeg"
with patch("streamlit.file_uploader", return_value=uploaded):
    runpy.run_path("/app/app.py", run_name="__main__")
'''
app = AppTest.from_string(script, default_timeout=90).run()
assert not app.exception, app.exception
app.button[0].click().run()
assert not app.exception, app.exception
assert not app.error, app.error
assert len(app.success) == 1, "Prediction did not appear"
print(app.success[0].value)

# A connection failure should give a readable message, not a traceback.
failure_script = script.replace(
    'with patch("streamlit.file_uploader", return_value=uploaded):',
    'import requests\nwith patch("requests.post", side_effect=requests.ConnectionError), '
    'patch("streamlit.file_uploader", return_value=uploaded):',
)
failed = AppTest.from_string(failure_script, default_timeout=90).run()
failed.button[0].click().run()
assert not failed.exception, failed.exception
assert "unavailable" in failed.error[0].value
print("Connection error handled correctly")
