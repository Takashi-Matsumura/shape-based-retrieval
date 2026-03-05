"""Runtime hook to patch Gradio for PyInstaller compatibility.

Gradio's component_meta.create_or_modify_pyi tries to read .py source files
at import time to generate .pyi type stubs. This fails in a PyInstaller bundle.
We intercept the import and patch it without triggering the full Gradio import.
"""
import sys


class _GradioPatcher:
    """Meta path finder that patches gradio.component_meta on import."""

    def find_module(self, fullname, path=None):
        if fullname == 'gradio.component_meta':
            return self
        return None

    def load_module(self, fullname):
        # Remove self to avoid infinite recursion
        sys.meta_path.remove(self)
        # Let the real import happen
        import importlib
        mod = importlib.import_module(fullname)
        # Patch the problematic function
        mod.create_or_modify_pyi = lambda *a, **kw: None
        sys.modules[fullname] = mod
        return mod


sys.meta_path.insert(0, _GradioPatcher())
