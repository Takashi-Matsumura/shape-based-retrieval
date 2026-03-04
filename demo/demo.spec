# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for CAD Search Demo."""

import os
import sys
from pathlib import Path

block_cipher = None

demo_dir = os.path.dirname(os.path.abspath(SPEC))

a = Analysis(
    [os.path.join(demo_dir, 'app.py')],
    pathex=[demo_dir],
    binaries=[],
    datas=[
        (os.path.join(demo_dir, 'data'), 'data'),
    ],
    hiddenimports=[
        'gradio',
        'gradio.routes',
        'gradio.themes',
        'plotly',
        'trimesh',
        'onnxruntime',
        'scipy.spatial',
        'scipy.spatial.transform',
        'numpy',
        'uvicorn',
        'starlette',
        'fastapi',
        'pydantic',
        'httpx',
        'anyio',
        'anyio._backends',
        'anyio._backends._asyncio',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'torch',
        'torchvision',
        'torchaudio',
        'tensorflow',
        'keras',
        'cv2',
        'matplotlib',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='CADSearchDemo',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='CADSearchDemo',
)
