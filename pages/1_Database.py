import streamlit as st
import pandas as pd
import os
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Database",
    layout="wide"
)

st.title("🧬 TCM Database")

# =========================================================
# 🧪 LIGAND DATABASE
# =========================================================

st.subheader("🧪 Ligand Database")

ligand_path = "data/ligands.csv"

if not os.path.exists(ligand_path):

    st.error("❌ ligands.csv not found")

    st.stop()

df = pd.read_csv(ligand_path)

# =========================================================
# SEARCH
# =========================================================

search = st.text_input(
    "🔍 Search (herb / pinyin / property / compound)"
)

if search:

    search_cols = [
        "herb_en",
        "herb_cn",
        "pinyin",
        "property",
        "compound"
    ]

    mask = False

    for col in search_cols:

        if col in df.columns:

            mask = mask | df[col].astype(str).str.contains(
                search,
                case=False,
                na=False
            )

    df = df[mask]

# =========================================================
# SHOW TABLE
# =========================================================

st.dataframe(
    df,
    use_container_width=True
)

# =========================================================
# SELECT LIGAND
# =========================================================

if not df.empty:

    selected_ligand = st.selectbox(
        "Select compound",
        df["compound"]
    )

    row = df[
        df["compound"] == selected_ligand
    ].iloc[0]

    st.write(f"💊 Selected: {row['compound']}")

    st.code(row["smiles"])

    if st.button("🚀 Send Ligand to Docking"):

        st.session_state[
            "selected_smiles"
        ] = row["smiles"]

        st.session_state[
            "selected_name"
        ] = row["compound"]

        st.success("Ligand sent!")

        st.switch_page("app.py")

# =========================================================
# 🧬 PROTEIN DATABASE
# =========================================================

st.markdown("---")

st.subheader("🧬 Protein Database")

protein_csv = "data/proteins.csv"

protein_dir = "proteins"

# =========================================================
# CHECK FILES
# =========================================================

if not os.path.exists(protein_csv):

    st.error("❌ proteins.csv not found")

    st.stop()

if not os.path.exists(protein_dir):

    st.error("❌ proteins folder not found")

    st.stop()

# =========================================================
# LOAD CSV
# =========================================================

pdf = pd.read_csv(protein_csv)

# =========================================================
# AUTO CREATE filename COLUMN
# =========================================================

if "filename" not in pdf.columns:

    pdf["filename"] = pdf["PDB"] + "_clean.pdb"

# =========================================================
# SEARCH
# =========================================================

search_p = st.text_input("🔍 Search protein")

if search_p:

    pdf = pdf[
        pdf.apply(
            lambda r:
            r.astype(str)
            .str.contains(
                search_p,
                case=False
            )
            .any(),
            axis=1
        )
    ]

# =========================================================
# SHOW TABLE
# =========================================================

st.dataframe(
    pdf,
    use_container_width=True
)

# =========================================================
# SELECT PROTEIN
# =========================================================

if not pdf.empty:

    selected = st.selectbox(
        "Select Protein",
        pdf["filename"]
    )

    row = pdf[
        pdf["filename"] == selected
    ].iloc[0]

    # =====================================================
    # DISPLAY INFO
    # =====================================================

    st.markdown(
        f"### 🧬 {row['Protein']}"
    )

    if "Function" in row:

        st.write(
            f"📖 {row['Function']}"
        )

    protein_path = os.path.join(
        protein_dir,
        selected
    )

    # =====================================================
    # 3D VIEW
    # =====================================================

    st.subheader("🧪 3D Visualization")

    if not os.path.exists(protein_path):

        st.error(
            f"❌ File not found: {protein_path}"
        )

    else:

        pdb_data = open(
            protein_path
        ).read()

        html = f"""
        <script src="https://unpkg.com/ngl@latest/dist/ngl.js"></script>

        <div id="viewport"
             style="width:100%; height:450px;">
        </div>

        <script>

        var stage = new NGL.Stage("viewport");

        var blob = new Blob(
            [`{pdb_data}`],
            {{type:'text/plain'}}
        );

        stage.loadFile(
            blob,
            {{ext:"pdb"}}
        ).then(function(o) {{

            o.addRepresentation(
                "cartoon",
                {{color:"skyblue"}}
            );

            o.autoView();

        }});

        </script>
        """

        components.html(
            html,
            height=450
        )

    # =====================================================
    # DOWNLOAD
    # =====================================================

    st.subheader("⬇️ Download Protein")

    if os.path.exists(protein_path):

        with open(protein_path, "rb") as f:

            st.download_button(
                label="Download PDB",
                data=f,
                file_name=selected,
                mime="chemical/x-pdb"
            )

    # =====================================================
    # SEND TO DOCKING
    # =====================================================

    if st.button("🚀 Send Protein to Docking"):

        st.session_state[
            "selected_protein"
        ] = selected

        st.success("Protein sent!")

        st.switch_page("app.py")
