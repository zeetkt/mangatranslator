import _env  # must be first — sets local cache paths
import shutil
from pathlib import Path
import gradio as gr
from main import translate_manga_page
from config import LANGUAGE_MAP, INPUT_DIR, OUTPUT_DIR, GRADIO_PORT, GRADIO_SHARE


def process_images(files, source_lang, target_lang, progress=gr.Progress()):
    if not files:
        raise gr.Error("No files uploaded")

    results = []
    progress((0, len(files)), desc="Starting...")

    for i, f in enumerate(files):
        name = Path(f.name).name
        progress((i, len(files)), desc=f"Processing {name} ({i+1}/{len(files)})...")

        src_copy = INPUT_DIR / f"_ui_{name}"
        shutil.copy2(f.name, src_copy)

        stem = src_copy.stem
        out_path = OUTPUT_DIR / f"{stem}_translated.png"

        translate_manga_page(
            str(src_copy), str(out_path),
            source_lang=source_lang,
            target_lang=target_lang,
        )

        src_copy.unlink(missing_ok=True)

        if out_path.exists():
            results.append((str(out_path), str(out_path)))
        else:
            results.append((str(src_copy), str(src_copy)))

    progress((len(files), len(files)), desc="Done!")
    return results


def build_ui():
    lang_choices = list(LANGUAGE_MAP.keys())

    with gr.Blocks(title="Manga Translator") as demo:
        gr.Markdown("# 📖 Manga Translator")

        with gr.Row():
            with gr.Column(scale=1):
                source_lang = gr.Dropdown(
                    choices=lang_choices, value="Japanese",
                    label="Source Language"
                )
                target_lang = gr.Dropdown(
                    choices=lang_choices, value="English",
                    label="Target Language"
                )

            with gr.Column(scale=2):
                files = gr.File(
                    file_count="multiple",
                    label="Upload Manga Page(s)",
                    file_types=[".png", ".jpg", ".jpeg", ".webp", ".bmp"],
                )

        translate_btn = gr.Button("Translate", variant="primary", size="lg")

        gallery = gr.Gallery(
            label="Results (before → after)",
            columns=4,
            object_fit="contain",
            height="auto",
        )

        translate_btn.click(
            fn=process_images,
            inputs=[files, source_lang, target_lang],
            outputs=gallery,
        )

    return demo


if __name__ == "__main__":
    INPUT_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)
    demo = build_ui()
    demo.launch(server_port=GRADIO_PORT, share=GRADIO_SHARE)
