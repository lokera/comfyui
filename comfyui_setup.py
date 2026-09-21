"""Ideal Informática - ComfyUI + Wan 2.2 TI2V-5B for T4 / social video.

Heavy files: /content/ComfyUI (VM)
Generated output: /content/drive/MyDrive/ComfyUI-Output
Code/workflows: GitHub
"""
from __future__ import annotations

import shutil
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path

WORKSPACE = Path("/content/ComfyUI")
DRIVE_OUTPUT = Path("/content/drive/MyDrive/ComfyUI-Output")
LOCAL_OUTPUT = WORKSPACE / "output"
REPO = "https://github.com/Comfy-Org/ComfyUI.git"
SETUP_VIDEO_URL = "https://raw.githubusercontent.com/lokera/comfyui/main/scripts/install_wan22_t4.py"
WORKFLOW_PATCH_URL = "https://raw.githubusercontent.com/lokera/comfyui/main/scripts/install_wan22_workflow.py"
CLOUDFLARED_URL = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb"

# ======== OPTIONS ========
USE_GOOGLE_DRIVE = True
UPDATE_COMFY_UI = True
INSTALL_COMFYUI_MANAGER = False
INSTALL_WAN22_T4 = True
INSTALL_CLOUDFLARED = True
START_COMFYUI = True


def log(msg: str) -> None:
    print(f"[IDEAL] {msg}", flush=True)


def run(cmd: list[str], cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess:
    log("$ " + " ".join(cmd))
    return subprocess.run(cmd, cwd=str(cwd) if cwd else None, check=check, text=True)


def mount_drive() -> None:
    if not USE_GOOGLE_DRIVE:
        return
    from google.colab import drive  # type: ignore
    log("Montando Google Drive...")
    drive.mount("/content/drive")
    DRIVE_OUTPUT.mkdir(parents=True, exist_ok=True)
    log(f"Saída do ComfyUI: {DRIVE_OUTPUT}")


def install_comfyui() -> None:
    if not (WORKSPACE / ".git").exists():
        log("Clonando ComfyUI para o armazenamento da VM...")
        run(["git", "clone", REPO, str(WORKSPACE)])
    elif UPDATE_COMFY_UI:
        log("Atualizando ComfyUI...")
        run(["git", "pull", "--ff-only"], cwd=WORKSPACE, check=False)

    # Não força xformers nem wheels CUDA antigas. A versão atual do
    # ComfyUI define suas dependências em requirements.txt.
    log("Instalando dependências atuais do ComfyUI...")
    run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], cwd=WORKSPACE)


def install_manager() -> None:
    if not INSTALL_COMFYUI_MANAGER:
        return
    manager = WORKSPACE / "custom_nodes" / "ComfyUI-Manager"
    if not manager.exists():
        run(["git", "clone", "https://github.com/Comfy-Org/ComfyUI-Manager.git", str(manager)])
    req = manager / "requirements.txt"
    if req.exists():
        run([sys.executable, "-m", "pip", "install", "-r", str(req)], check=False)


def install_wan22_t4() -> None:
    if not INSTALL_WAN22_T4:
        return
    installer = WORKSPACE / ".ideal_install_wan22_t4.py"
    workflow_patcher = WORKSPACE / ".ideal_install_wan22_workflow.py"
    log("Baixando instalador Wan 2.2 TI2V-5B do GitHub...")
    run(["curl", "-L", "--fail", "--retry", "3", SETUP_VIDEO_URL, "-o", str(installer)])
    run([sys.executable, str(installer)])
    installer.unlink(missing_ok=True)

    log("Baixando workflow oficial do ComfyUI e aplicando perfil T4...")
    run(["curl", "-L", "--fail", "--retry", "3", WORKFLOW_PATCH_URL, "-o", str(workflow_patcher)])
    run([sys.executable, str(workflow_patcher)])
    workflow_patcher.unlink(missing_ok=True)


def link_output() -> None:
    if not USE_GOOGLE_DRIVE:
        return
    DRIVE_OUTPUT.mkdir(parents=True, exist_ok=True)
    if LOCAL_OUTPUT.is_symlink():
        try:
            if LOCAL_OUTPUT.resolve() == DRIVE_OUTPUT.resolve():
                log("Output já está ligado ao Google Drive.")
                return
        except FileNotFoundError:
            pass
        LOCAL_OUTPUT.unlink()
    elif LOCAL_OUTPUT.exists():
        stamp = time.strftime("%d%m%Y-%H-%Mh")
        backup = WORKSPACE.parent / f"ComfyUI_output_local_{stamp}"
        log(f"Preservando output local existente em: {backup}")
        shutil.move(str(LOCAL_OUTPUT), str(backup))
    LOCAL_OUTPUT.symlink_to(DRIVE_OUTPUT, target_is_directory=True)
    log("Output do ComfyUI agora fica somente no Google Drive.")


def install_cloudflared() -> None:
    if not INSTALL_CLOUDFLARED or shutil.which("cloudflared"):
        return
    deb = Path("/content/cloudflared-linux-amd64.deb")
    run(["curl", "-L", "--fail", "--retry", "3", CLOUDFLARED_URL, "-o", str(deb)])
    run(["apt-get", "update", "-y"])
    run(["apt-get", "install", "-y", str(deb)])
    deb.unlink(missing_ok=True)


def gpu_info() -> None:
    run(["nvidia-smi"], check=False)
    run([
        sys.executable, "-c",
        "import torch; print('Torch:',torch.__version__); print('CUDA:',torch.version.cuda); print('CUDA available:',torch.cuda.is_available()); print('GPU:',torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'); print('VRAM GB:', round(torch.cuda.get_device_properties(0).total_memory/1024**3,2) if torch.cuda.is_available() else 0)"
    ], check=False)


def wait_port(port: int, timeout: int = 180) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            if s.connect_ex(("127.0.0.1", port)) == 0:
                return True
        time.sleep(1)
    return False


def start_cloudflared(port: int) -> None:
    def worker() -> None:
        log("Iniciando Cloudflare Quick Tunnel...")
        proc = subprocess.Popen(
            ["cloudflared", "tunnel", "--protocol", "http2", "--url", f"http://127.0.0.1:{port}"],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1,
        )
        assert proc.stdout is not None
        for line in proc.stdout:
            line = line.rstrip()
            if "trycloudflare.com" in line:
                print(f"\n[COMFY-URL] {line}\n", flush=True)
            else:
                print(f"[CLOUDFLARED] {line}", flush=True)
    threading.Thread(target=worker, daemon=True).start()


def start_comfyui() -> None:
    port = 8188
    log("Iniciando ComfyUI com perfil low-VRAM para T4...")
    proc = subprocess.Popen([
        sys.executable, "main.py",
        "--listen", "127.0.0.1",
        "--port", str(port),
        "--lowvram",
        "--enable-cors-header", "*",
    ], cwd=str(WORKSPACE))
    if not wait_port(port):
        proc.terminate()
        raise RuntimeError("ComfyUI não abriu a porta 8188 dentro do prazo.")
    log("ComfyUI está ativo em 127.0.0.1:8188")
    if INSTALL_CLOUDFLARED:
        start_cloudflared(port)
    while proc.poll() is None:
        time.sleep(2)
    raise SystemExit(proc.returncode or 0)


def main() -> None:
    log("=== Ideal Informática | Image → Video | Wan 2.2 TI2V-5B | T4 ===")
    mount_drive()
    gpu_info()
    install_comfyui()
    install_manager()
    install_wan22_t4()
    link_output()
    install_cloudflared()
    if START_COMFYUI:
        start_comfyui()


if __name__ == "__main__":
    main()
