"""Install the Wan 2.2 TI2V-5B files used by ComfyUI's official 5B workflow.
Designed for a Tesla T4 16 GB first-pass profile.
"""
from __future__ import annotations
import hashlib
import subprocess
from pathlib import Path

ROOT = Path('/content/ComfyUI')
FILES = [
    {
        'name':'wan2.2_ti2v_5B_fp16.safetensors',
        'url':'https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/diffusion_models/wan2.2_ti2v_5B_fp16.safetensors',
        'path':ROOT/'models/diffusion_models/wan2.2_ti2v_5B_fp16.safetensors',
        'sha256':'456f901338bd9eadbded3828b819109a9b68e8a525ca5cf8d0049a69fcfeca1e',
        'size':9999658848,
    },
    {
        'name':'umt5_xxl_fp8_e4m3fn_scaled.safetensors',
        'url':'https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors',
        'path':ROOT/'models/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors',
        'sha256':'c3355d30191f1f066b26d93fba017ae9809dce6c627dda5f6a66eaa651204f68',
        'size':0,
    },
    {
        'name':'wan2.2_vae.safetensors',
        'url':'https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/vae/wan2.2_vae.safetensors',
        'path':ROOT/'models/vae/wan2.2_vae.safetensors',
        'sha256':'e40321bd36b9709991dae2530eb4ac303dd168276980d3e9bc4b6e2b75fed156',
        'size':1409400960,
    },
]

def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(8*1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()

def ensure(item: dict) -> None:
    p=item['path']; p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists():
        print(f"[WAN22] Verificando {item['name']} ...", flush=True)
        if sha256(p) == item['sha256']:
            print(f"[WAN22] OK {item['name']}", flush=True)
            return
        print(f"[WAN22] Hash inválido; removendo arquivo incompleto/corrompido.", flush=True)
        p.unlink()
    print(f"[WAN22] Baixando {item['name']}", flush=True)
    subprocess.run([
        'wget','-c','--show-progress','--timeout=60','--tries=10',
        item['url'],'-O',str(p)
    ], check=True)
    got=sha256(p)
    if got != item['sha256']:
        p.unlink(missing_ok=True)
        raise RuntimeError(f"SHA256 inválido para {item['name']}: {got}")
    print(f"[WAN22] Pronto: {p}", flush=True)

for item in FILES:
    ensure(item)

print('[WAN22] Todos os arquivos do Wan 2.2 TI2V-5B estão prontos.')
