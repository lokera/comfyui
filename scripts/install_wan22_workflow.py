"""Download ComfyUI's official Wan 2.2 TI2V-5B workflow and make a T4/social profile.

The official template is downloaded at runtime so this project does not copy vendor workflow JSON into Git.
"""
from __future__ import annotations
import json
import subprocess
from pathlib import Path

WORKSPACE=Path('/content/ComfyUI')
RAW_URL='https://raw.githubusercontent.com/Comfy-Org/workflow_templates/main/templates/video_wan2_2_5B_ti2v.json'
TARGET=WORKSPACE/'user/default/workflows/Wan2.2_I2V_T4_Social.json'
TEMP=WORKSPACE/'.wan2_2_official.json'

TARGET.parent.mkdir(parents=True, exist_ok=True)
print('[WORKFLOW] Baixando template oficial do ComfyUI...')
subprocess.run(['curl','-L','--fail','--retry','3',RAW_URL,'-o',str(TEMP)],check=True)

data=json.loads(TEMP.read_text(encoding='utf-8'))
for node in data.get('nodes',[]):
    ntype=node.get('type')
    if ntype=='Wan22ImageToVideoLatent':
        # T4 first-pass: vertical-ish 9:16 and a short clip.
        node['widgets_values']=[320,576,49,1]
    elif ntype=='CreateVideo':
        node['widgets_values']=[24]
    elif ntype=='SaveVideo':
        node['widgets_values']=['video/IdealSocial','auto','auto']
    elif ntype=='LoadImage':
        node['widgets_values']=['social_input.png','image']
    elif ntype=='CLIPTextEncode' and node.get('title')=='CLIP Text Encode (Positive Prompt)':
        node['widgets_values']=[
            'Vertical social media commercial video. A stylish young woman in a clean modern studio looks naturally at the camera, gently shifts her weight, subtle hand movement, realistic hair and clothing movement, smooth slow camera push-in, stable face and body, natural lighting, polished advertising look, realistic motion, high detail.'
        ]
    elif ntype=='CLIPTextEncode' and node.get('title')=='CLIP Text Encode (Negative Prompt)':
        node['widgets_values']=[
            'flicker, jitter, camera shake, static image, frozen motion, deformed body, warped face, extra arms, extra legs, extra fingers, missing fingers, duplicated person, unstable anatomy, bad hands, text, subtitles, watermark, logo, low quality, blurry, noisy, oversaturated'
        ]
    elif ntype=='MarkdownNote':
        notes=node.get('widgets_values',[])
        if notes:
            notes[0] += '\n\n### Ideal Informática — perfil inicial T4\n320×576 • 49 frames • 24 FPS • ~2,0 s. Gere primeiro nessa configuração e só depois aumente resolução/duração.'

TARGET.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
TEMP.unlink(missing_ok=True)
print(f'[WORKFLOW] Instalado: {TARGET}')
