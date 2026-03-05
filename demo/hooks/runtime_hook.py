"""Runtime hook to patch Gradio for PyInstaller compatibility.

Gradio's component_meta.create_or_modify_pyi tries to read .py source files
at import time to generate .pyi type stubs. This fails in a PyInstaller bundle
because source files are not available. We patch it to be a no-op.
"""
import gradio.component_meta as _cm

_cm.create_or_modify_pyi = lambda *args, **kwargs: None
