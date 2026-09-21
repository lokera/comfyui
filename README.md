# Ideal Informática — ComfyUI + Wan 2.2 TI2V-5B + T4

Projeto para Google Colab com Tesla T4 16 GB, voltado a **Image → Video para redes sociais**.

## Arquitetura

```text
/content/ComfyUI/             ← ComfyUI, modelos, custom nodes: VM
/content/ComfyUI/output/      → symlink → Google Drive
/content/drive/MyDrive/ComfyUI-Output/
                                  ↑ somente resultados
```

## Estrutura do GitHub

```text
lokera/comfyui/
├── bootstrap.py
├── comfyui_setup.py
├── scripts/
│   ├── install_wan22_t4.py
│   └── install_wan22_workflow.py
└── workflows/
    └── README.md
```

## Célula mínima do Colab

```python
!wget -q -O /content/bootstrap.py https://raw.githubusercontent.com/lokera/comfyui/main/bootstrap.py
!python /content/bootstrap.py
```

## O que o setup faz

1. Monta o Google Drive apenas para `ComfyUI-Output`.
2. Instala/atualiza ComfyUI em `/content/ComfyUI`.
3. Não força versões antigas de PyTorch/xformers.
4. Baixa o Wan 2.2 TI2V-5B, UMT5 FP8 e Wan 2.2 VAE para a VM.
5. Baixa o workflow oficial do ComfyUI e cria um perfil T4 vertical.
6. Liga `ComfyUI/output` ao Google Drive.
7. Instala Cloudflared e inicia um Quick Tunnel.
8. Inicia ComfyUI em modo `--lowvram`.

## Primeiro teste

Coloque uma imagem vertical em:

`/content/ComfyUI/input/social_input.png`

Abra o workflow `Wan2.2_I2V_T4_Social.json`.

Configuração inicial:

| Parâmetro | Valor |
|---|---:|
| Resolução | 320 × 576 |
| Frames | 49 |
| FPS | 24 |
| Duração | ~2,0 s |

A ideia é primeiro validar geração e memória da T4. Depois aumentaremos gradualmente para um perfil de produção e adicionaremos upscale/montagem vertical 1080×1920.
