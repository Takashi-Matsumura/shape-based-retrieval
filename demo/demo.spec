# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for CAD Search Demo."""

import os
import sys
import importlib
import pkgutil
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

demo_dir = os.path.dirname(os.path.abspath(SPEC))

# Collect data files from all installed packages to avoid missing version.txt etc.
# Gradio and its dependencies (safehttpx, groovy, etc.) rely on package data files
all_extra_datas = []
for pkg_name in [
    'safehttpx', 'groovy', 'gradio_client',
    'semantic_version', 'tomlkit', 'orjson',
]:
    try:
        all_extra_datas += collect_data_files(pkg_name)
    except Exception:
        pass

# Gradio needs .py source files available at runtime (for create_or_modify_pyi)
try:
    all_extra_datas += collect_data_files('gradio', include_py_files=True)
except Exception:
    pass

a = Analysis(
    [os.path.join(demo_dir, 'app.py')],
    pathex=[demo_dir],
    binaries=[],
    datas=[
        (os.path.join(demo_dir, 'data'), 'data'),
    ] + all_extra_datas,
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
    runtime_hooks=[os.path.join(demo_dir, 'hooks', 'runtime_hook.py')],
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
