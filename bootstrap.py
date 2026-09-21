"""Ideal Informática - minimal Colab bootstrap.
This is the only cell that needs to be kept in the notebook.
"""
from pathlib import Path
import urllib.request
import runpy

SETUP_URL = "https://raw.githubusercontent.com/lokera/comfyui/main/comfyui_setup.py"
LOCAL_SETUP = Path("/content/comfyui_setup.py")

print("[BOOT] Baixando comfyui_setup.py do GitHub...")
urllib.request.urlretrieve(SETUP_URL, LOCAL_SETUP)
print(f"[BOOT] OK: {LOCAL_SETUP}")
runpy.run_path(str(LOCAL_SETUP), run_name="__main__")
