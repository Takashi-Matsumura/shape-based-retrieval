"""CAD Similar Shape Search Demo - Gradio Application."""

import logging
import tempfile
from pathlib import Path

import gradio as gr
import numpy as np
import plotly.graph_objects as go

from core.cad_processor import load_mesh, normalize_mesh, process_cad_file
from core.config import ALLOWED_EXTENSIONS, SAMPLES_DIR
from core.feature_extractor import extract_features
from core.similarity import search_similar

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def mesh_to_plotly(mesh, title: str = "", color: str = "#1f77b4") -> go.Figure:
    """Convert a trimesh mesh to a Plotly Mesh3d figure."""
    vertices = mesh.vertices
    faces = mesh.faces

    fig = go.Figure(data=[
        go.Mesh3d(
            x=vertices[:, 0],
            y=vertices[:, 1],
            z=vertices[:, 2],
            i=faces[:, 0],
            j=faces[:, 1],
            k=faces[:, 2],
            color=color,
            opacity=0.8,
            flatshading=True,
            lighting=dict(ambient=0.5, diffuse=0.8, specular=0.3),
            lightposition=dict(x=100, y=100, z=200),
        )
    ])

    fig.update_layout(
        title=dict(text=title, x=0.5, font=dict(size=12)),
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            aspectmode="data",
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.0)),
        ),
        margin=dict(l=0, r=0, t=30, b=0),
        height=300,
    )
    return fig


def empty_plot(text: str = "") -> go.Figure:
    """Create an empty placeholder plot."""
    fig = go.Figure()
    fig.update_layout(
        title=dict(text=text, x=0.5, font=dict(size=11, color="gray")),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        height=300,
        margin=dict(l=0, r=0, t=30, b=0),
    )
    return fig


def preview_file(file) -> go.Figure:
    """Generate a 3D preview of an uploaded CAD file."""
    if file is None:
        return empty_plot("Upload a file to preview")

    try:
        file_path = file.name if hasattr(file, "name") else str(file)
        ext = Path(file_path).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            return empty_plot(f"Unsupported format: {ext}")

        mesh = load_mesh(file_path)
        mesh = normalize_mesh(mesh)
        return mesh_to_plotly(mesh, "Query Model", color="#e74c3c")
    except Exception as e:
        return empty_plot(f"Error: {e}")


def do_search(file, top_k: int) -> list[go.Figure]:
    """Perform similarity search and return result plots."""
    results_plots = [empty_plot() for _ in range(10)]

    if file is None:
        return results_plots

    try:
        file_path = file.name if hasattr(file, "name") else str(file)
        ext = Path(file_path).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            results_plots[0] = empty_plot(f"Unsupported: {ext}")
            return results_plots

        # Process and extract features
        points, _, _ = process_cad_file(file_path)
        query_embedding = extract_features(points)

        # Search
        results = search_similar(query_embedding, top_k=int(top_k))

        # Build result plots
        for i, result in enumerate(results):
            if i >= 10:
                break
            sample_path = SAMPLES_DIR / result["filename"]
            if sample_path.exists():
                mesh = load_mesh(sample_path)
                mesh = normalize_mesh(mesh)
                title = (
                    f"#{i+1} {result['filename']}\n"
                    f"{result['category']} | {result['similarity']:.1%}"
                )
                # Color gradient: more similar = more green
                sim = result["similarity"]
                r_val = int(255 * (1 - sim))
                g_val = int(255 * sim)
                color = f"rgb({r_val},{g_val},80)"
                results_plots[i] = mesh_to_plotly(mesh, title, color=color)
            else:
                results_plots[i] = empty_plot(f"#{i+1} {result['filename']} (file missing)")

    except Exception as e:
        logger.exception("Search failed")
        results_plots[0] = empty_plot(f"Error: {e}")

    return results_plots


def build_ui() -> gr.Blocks:
    """Build the Gradio UI."""
    with gr.Blocks(
        title="CAD Similar Shape Search",
        theme=gr.themes.Soft(),
    ) as demo:
        gr.Markdown("# CAD Similar Shape Search Demo")
        gr.Markdown(
            "Upload an STL or OBJ file to find similar shapes from the sample database."
        )

        # --- Query section ---
        with gr.Row():
            with gr.Column(scale=1):
                file_input = gr.File(
                    label="Upload CAD File (.stl, .obj)",
                    file_types=[".stl", ".obj"],
                )
                top_k_slider = gr.Slider(
                    minimum=1, maximum=10, value=5, step=1,
                    label="Number of results (top-k)",
                )
                search_btn = gr.Button("Search", variant="primary", size="lg")

            with gr.Column(scale=2):
                query_plot = gr.Plot(label="Query Model Preview")

        # --- Results section ---
        gr.Markdown("## Search Results")
        result_plots = []
        for row_idx in range(2):
            with gr.Row():
                for col_idx in range(5):
                    idx = row_idx * 5 + col_idx
                    p = gr.Plot(label=f"Result #{idx+1}")
                    result_plots.append(p)

        # --- Events ---
        file_input.change(
            fn=preview_file,
            inputs=[file_input],
            outputs=[query_plot],
        )

        search_btn.click(
            fn=do_search,
            inputs=[file_input, top_k_slider],
            outputs=result_plots,
        )

    return demo


if __name__ == "__main__":
    app = build_ui()
    app.launch(inbrowser=True, server_name="127.0.0.1", server_port=7860)
