import streamlit as st
import re
import io
import pandas as pd
from deidentifier import deidentify_text, redact_allergies, decrypt_mapping, decrypt_value, encrypt_mapping, encrypt_value
from reidentifier import reidentify_text, convert_starred_to_placeholders

st.set_page_config(page_title="PHI Redactor", layout="wide")
st.title("PHI Redactor: De-identification & Re-identification Tool")

st.markdown("""
Welcome to the **PHI Redactor Tool**! 🛡️
This app allows you to **de-identify** and **re-identify** Protected Health Information (PHI) from medical text files.
##### 🔍 Features:
""")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("###### **De-identification** tab:")
    st.markdown("""
    - Upload a medical `.txt` file
    - Automatically redacts PHI 
    - Download both:
        - The fully redacted file (with secure placeholders)
        - An encrypted mapping CSV for safe re-identification later
    """)

with col2:
    st.markdown("###### **Re-identification** tab:")
    st.markdown("""
    - Paste in a redacted file preview
    - Automatically restores the original PHI from your current session’s mapping
    """)

with col3:
    st.markdown("###### **Reidentify Old File** tab:")
    st.markdown("""
    - Reconstruct an old de-identified file by uploading:
        - The redacted `.txt` file
        - The corresponding encrypted mapping CSV
    """)

# Session-state-based mapping store
if "mapping" not in st.session_state:
    st.session_state["mapping"] = {}

# Menu
tab1, tab2, tab3 = st.tabs(["De-identification", "Re-identification", "Reidentify Old File"])

# Deidentifier tab
with tab1:
    st.header("De-identify Medical Files")
    uploaded_file = st.file_uploader("Upload a Medical Text File", type="txt")
    file_basename = uploaded_file.name.rsplit(".", 1)[0] if uploaded_file else "output"
    st.session_state["file_basename"] = file_basename

    if uploaded_file:
        raw_text = uploaded_file.read().decode("utf-8")
        st.subheader("Original Text")
        st.text_area("Original Medical Note", raw_text, height=250)

        if st.button("De-identify"):
            redacted, mapping = deidentify_text(raw_text)
            redacted, mapping = redact_allergies(redacted, mapping)

            st.session_state["mapping"] = mapping
            st.session_state["redacted_text"] = redacted
            st.session_state["pretty_display"] = re.sub(r"__([A-Z]+)#\d+__", lambda m: f"*{m.group(1)}*", redacted)
            st.session_state["mapping_df"] = pd.DataFrame(
                { "Tag": list(mapping.keys()), "Encrypted Value": [encrypt_value(v) for v in mapping.values()] }
            )
            st.session_state["deidentified_done"] = True
    
    if st.session_state.get("deidentified_done", False):
        st.subheader("De-identified Text (Preview)")
        st.text_area("Copy and paste this into the Re-identify tab →", st.session_state["pretty_display"], height=250)

        buffer = io.BytesIO()
        st.session_state["mapping_df"].to_csv(buffer, index=False)
        buffer.seek(0)
        st.download_button(
            label="Download Mapping CSV",
            data=buffer,
            file_name=f"{file_basename}_mapping.csv",
            mime="text/csv"
        )

        st.download_button(
            label="Download De-identified Text",
            data=st.session_state["redacted_text"],
            file_name=f"{file_basename}_deidentified.txt",
            mime="text/plain"
        )

        # Optional: Show decrypted mapping
        if st.checkbox("Show Mapping Information"):
            display_df = pd.DataFrame(list(st.session_state["mapping"].items()), columns=["Tag", "Original Value"])
            st.dataframe(display_df)

# Reidentifier tab
with tab2:
    st.header("Re-identify Medical Files")
    file_basename = st.session_state.get("file_basename", "output")
    reid_input = st.text_area("Paste De-identified Text Here", height=250)
    if st.button("Re-identify"):
        mapping = st.session_state.get("mapping", {})
        if not mapping:
            st.error("⚠️ Mapping not found. Please de-identify a file first.")
        else:
            converted = convert_starred_to_placeholders(reid_input, mapping)
            restored_text = reidentify_text(converted, mapping)
            st.subheader("Re-identified Output")
            st.text_area("Restored Medical Note", restored_text, height=250)

            st.download_button(
                label="📄 Download Re-identified Text",
                data=restored_text,
                file_name=f"{file_basename}_reidentified.txt",
                mime="text/plain"
            )

#Reidentify old files
with tab3:
    st.header("Re-identify Medical Files")
    st.markdown("""
    Upload a de-identified file **and** the corresponding mapping CSV to restore the original content with PHI information.
    """)

    reidentify_file = st.file_uploader("Upload de-identified text file", type=["txt"], key="reidentify_uploader")
    mapping_file = st.file_uploader("Upload corresponding mapping file (CSV)", type=["csv"], key="mapping_uploader")

    if reidentify_file is not None:
        reidentify_content = reidentify_file.getvalue().decode("utf-8")

        # Convert __LABEL#X__ to *LABEL* for preview
        pretty_display = re.sub(r"__([A-Z]+)#\d+__", lambda m: f"*{m.group(1)}*", reidentify_content)

        st.subheader("De-identified Content")
        st.text_area("", pretty_display, height=200, key="reidentify_display", disabled=True)

        if mapping_file is not None:
            mapping_df = pd.read_csv(mapping_file)
            
            # After reading the CSV into mapping_df
            encrypted_mapping = dict(zip(mapping_df['Tag'], mapping_df['Encrypted Value']))
            decrypted_mapping = {k: decrypt_value(v) for k, v in encrypted_mapping.items()}
            mapping = decrypted_mapping

            # Process re-identification
            reidentified_text = reidentify_text(reidentify_content, mapping)
            st.subheader("Re-identified Content")
            st.text_area("", reidentified_text, height=200, key="reidentified_text", disabled=True)

            # Provide download for re-identified file
            buffer = io.BytesIO()
            buffer.write(reidentified_text.encode())
            buffer.seek(0)

            filename = reidentify_file.name.split(".")[0] + "_reidentified.txt"
            st.download_button(
                label="Download Re-identified File",
                data=buffer,
                file_name=filename,
                mime="text/plain"
            )

            st.success("Re-identification successful!")
