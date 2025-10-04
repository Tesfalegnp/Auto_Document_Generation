# streamlit_app.py
import streamlit as st
import tempfile
import zipfile
import shutil
import subprocess
import sys
import os
import io
from pathlib import Path
import streamlit.components.v1 as components
import shlex

st.set_page_config(page_title="Auto Document Generator", layout="wide")

PROJECT_ROOT = Path(__file__).parent.resolve()
RUN_DOCS_SCRIPT = PROJECT_ROOT / "run_docs.py"

st.title("Auto Document Generation — Web UI")
st.write("Upload a zipped project and this app will run the documentation pipeline and show results.")

uploaded = st.file_uploader("Upload project as ZIP", type=["zip"], help="Compress your project folder to .zip and upload here.")

col1, col2 = st.columns(2)
with col1:
    skip_build = st.checkbox("Skip building parsers (`--skip-build`)", value=False)
    no_open_hint = st.checkbox("Don't open HTML (recommended for server)", value=True)
with col2:
    extra_args = st.text_input("Extra args for run_docs.py (optional)", value="", placeholder="e.g. --some-flag value")
    show_verbose = st.checkbox("Show run logs (stdout/stderr)", value=True)

generate_btn = st.button("Generate docs")

def find_project_root(extract_dir: Path) -> Path:
    # If the zip contains a single top-level folder, use it as project root
    entries = [p for p in extract_dir.iterdir() if p.name not in ("__MACOSX", ".DS_Store")]
    if len(entries) == 1 and entries[0].is_dir():
        return entries[0]
    return extract_dir

if uploaded is not None:
    # Save uploaded file
    tmp_zip = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
    try:
        tmp_zip.write(uploaded.getbuffer())
        tmp_zip.flush()
        tmp_zip.close()
    except Exception as e:
        st.error(f"Failed saving uploaded file: {e}")
        raise

    st.info("Uploaded zip saved. Ready to extract.")
    st.write("File name:", uploaded.name)

    # Show a preview button to inspect contents
    if st.button("List zip contents"):
        try:
            with zipfile.ZipFile(tmp_zip.name, "r") as zf:
                files = zf.namelist()[:200]
            st.write("Sample of zip contents (first 200 entries):")
            st.write(files)
        except Exception as e:
            st.error(f"Cannot read zip: {e}")

    if generate_btn:
        # Create a unique extraction folder
        extract_dir = Path(tempfile.mkdtemp(prefix="uploaded_proj_"))
        st.info(f"Extracting to: {extract_dir}")
        try:
            with zipfile.ZipFile(tmp_zip.name, "r") as zf:
                zf.extractall(path=str(extract_dir))
        except Exception as e:
            st.error(f"Failed to extract zip: {e}")
            raise

        project_root = find_project_root(extract_dir)
        st.success(f"Detected project root: {project_root}")

        # Build the command to call run_docs.py
        cmd = [sys.executable, str(RUN_DOCS_SCRIPT), "--root", str(project_root)]
        if skip_build:
            cmd.append("--skip-build")
        if no_open_hint:
            cmd.append("--no-open")
        if extra_args:
            try:
                cmd += shlex.split(extra_args)
            except Exception:
                cmd += [extra_args]

        st.write("Running pipeline command:")
        st.code(" ".join(map(str, cmd)))

        # Run the process and capture output
        with st.spinner("Running documentation pipeline (this can take a minute or more)..."):
            try:
                proc = subprocess.run(cmd, cwd=str(PROJECT_ROOT), capture_output=True, text=True)
            except Exception as e:
                st.error(f"Failed to run pipeline: {e}")
                # cleanup
                try:
                    shutil.rmtree(extract_dir)
                except Exception:
                    pass
                raise

        if show_verbose:
            st.subheader("Process output")
            st.markdown("**STDOUT**")
            st.code(proc.stdout if proc.stdout else "<no stdout>")
            st.markdown("**STDERR**")
            st.code(proc.stderr if proc.stderr else "<no stderr>")

        if proc.returncode != 0:
            st.error(f"Pipeline failed with exit code {proc.returncode}. See logs above.")
        else:
            st.success("Pipeline completed successfully.")

        # Show generated README (if exists)
        generated_readme = PROJECT_ROOT / "README_docs.md"
        if generated_readme.exists():
            st.subheader("Generated README (`README_docs.md`)")
            try:
                txt = generated_readme.read_text(encoding="utf-8")
                st.markdown(txt, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Failed to load README_docs.md: {e}")
        else:
            st.warning("README_docs.md not found in app root after pipeline.")

        # Show generated HTML (if exists)
        generated_html = PROJECT_ROOT / "docs" / "index.html"
        if generated_html.exists():
            st.subheader("Generated HTML (`docs/index.html`) preview")
            try:
                html_text = generated_html.read_text(encoding="utf-8")
                # Embed the HTML. Note: relative asset paths (css/img) might not load; see notes.
                components.html(html_text, height=800, scrolling=True)
            except Exception as e:
                st.error(f"Failed to show HTML preview: {e}")
        else:
            st.info("No docs/index.html found. Maybe md->html step was skipped or failed.")

        # Offer a download for the produced docs/ folder (zipped)
        docs_dir = PROJECT_ROOT / "docs"
        if docs_dir.exists():
            st.subheader("Download generated docs")
            zip_buf = io.BytesIO()
            try:
                with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zfh:
                    for root, _, files in os.walk(docs_dir):
                        for f in files:
                            full = Path(root) / f
                            rel = full.relative_to(docs_dir)
                            zfh.write(full, arcname=str(rel))
                zip_buf.seek(0)
                st.download_button("Download docs as ZIP", data=zip_buf, file_name="docs.zip")
            except Exception as e:
                st.error(f"Failed to create docs ZIP: {e}")
        else:
            st.info("No docs directory to download.")

        # Cleanup uploaded/extracted files
        try:
            os.remove(tmp_zip.name)
        except Exception:
            pass
        try:
            shutil.rmtree(extract_dir)
        except Exception:
            pass

        st.info("Temporary files cleaned up.")
