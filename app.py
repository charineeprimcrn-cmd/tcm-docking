import streamlit as st
import os
import glob
import shutil
import subprocess
import streamlit.components.v1 as components

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="TCM Docking Platform",
    layout="wide"
)

st.title("🧬 TCM Docking Platform")

# =====================================================
# FUNCTIONS
# =====================================================

def run_command(cmd):

    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True
    )

    return result.stdout, result.stderr


def extract_affinity(file):

    try:

        with open(file) as f:

            for line in f:

                if "REMARK VINA RESULT" in line:

                    return float(line.split()[3])

    except:

        return None


# =====================================================
# AUTO GRID DATABASE
# =====================================================

protein_grids = {

    "1M17": (21.5, 24.5, 29.5),
    "2OJJ": (35, 40, 45),
    "4EY7": (90, 85, 70),
    "6LU7": (-10, 12, 68),
    "6M0J": (-26, 18, 10),
    "5IKR": (23, 45, 12),

    "1NFI": (15, 22, 30),
    "1DGF": (20, 25, 35),
    "2AZ5": (10, 18, 28),
    "2C9V": (14, 16, 24),
    "4FA6": (30, 40, 50),
    "2ZHV": (12, 20, 32),
    "2V5Z": (25, 35, 45),
    "3E7G": (22, 18, 27),
    "6NPY": (19, 24, 31),
    "3CS8": (17, 28, 40),
    "2ONC": (15, 15, 15),
    "3WZE": (28, 30, 34),
    "4BBE": (11, 21, 33),
    "4CFE": (26, 36, 46),
}

# =====================================================
# 3D VIEWER
# =====================================================

def show_3d():

    if not os.path.exists("work/protein.pdb"):
        st.warning("No protein structure")
        return

    if not os.path.exists("work/result.pdb"):
        st.warning("No docking result")
        return

    protein = open("work/protein.pdb").read()
    ligand = open("work/result.pdb").read()

    html = f"""
    <script src="https://unpkg.com/ngl@latest/dist/ngl.js"></script>

    <div id="viewport" style="width:100%; height:600px;"></div>

    <script>

    var stage = new NGL.Stage("viewport");

    var proteinBlob = new Blob(
        [`{protein}`],
        {{type:'text/plain'}}
    );

    var ligandBlob = new Blob(
        [`{ligand}`],
        {{type:'text/plain'}}
    );

    stage.loadFile(proteinBlob, {{ext:"pdb"}})
    .then(function(o) {{

        o.addRepresentation(
            "cartoon",
            {{
                color:"skyblue",
                sele:"protein"
            }}
        );

        o.autoView();
    }});

    stage.loadFile(ligandBlob, {{ext:"pdb"}})
    .then(function(o) {{

        o.addRepresentation(
            "ball+stick",
            {{color:"red"}}
        );
    }});

    </script>
    """

    components.html(html, height=600)

# =====================================================
# LAYOUT
# =====================================================

col1, col2 = st.columns(2)

# =====================================================
# LEFT PANEL
# =====================================================

with col1:

    st.subheader("📥 Input")

    # =================================================
    # PROTEIN DATABASE
    # =================================================

    st.subheader("🧬 Protein Database")

    BASE_DIR = os.path.dirname(
        os.path.abspath(__file__)
    )

    protein_folder = os.path.join(
        BASE_DIR,
        "proteins"
    )

    protein_files = sorted(
        glob.glob(f"{protein_folder}/*.pdb")
    )

    # filter only clean pdb
    protein_files = [
        f for f in protein_files
        if "_clean.pdb" in f
    ]

    if len(protein_files) == 0:

        st.error("No proteins found")

        st.stop()

    protein_names = [

        os.path.basename(f)

        for f in protein_files
    ]

    selected_protein = st.selectbox(
        "Select Protein",
        protein_names
    )

    protein_path = os.path.join(
        protein_folder,
        selected_protein
    )

    st.success(f"Loaded: {selected_protein}")

    # =================================================
    # LIGAND
    # =================================================

    st.subheader("🧪 Ligand")

    ligand_mode = st.radio(
        "Ligand Source",
        ["Upload", "Database"]
    )

    ligand_file = None
    smiles = None

    # =================================================
    # UPLOAD
    # =================================================

    if ligand_mode == "Upload":

        ligand_file = st.file_uploader(
            "Upload Ligand (.smi/.pdbqt)"
        )

    # =================================================
    # DATABASE
    # =================================================

    else:

        if "selected_smiles" in st.session_state:

            smiles = st.session_state[
                "selected_smiles"
            ]

            st.success(
                f"Selected: "
                f"{st.session_state.get('selected_name','')}"
            )

            st.code(smiles)

        else:

            st.warning("No ligand selected")

    # =================================================
    # GRID
    # =================================================

    st.subheader("📦 Grid Settings")

    grid_mode = st.radio(
        "Grid Mode",
        ["Auto", "Manual"]
    )

    # =================================================
    # MANUAL
    # =================================================

    if grid_mode == "Manual":

        cx = st.number_input(
            "center_x",
            value=0.0
        )

        cy = st.number_input(
            "center_y",
            value=0.0
        )

        cz = st.number_input(
            "center_z",
            value=0.0
        )

        sx = st.number_input(
            "size_x",
            value=20
        )

        sy = st.number_input(
            "size_y",
            value=20
        )

        sz = st.number_input(
            "size_z",
            value=20
        )

# =====================================================
# RIGHT PANEL
# =====================================================

with col2:

    st.subheader("📊 Result")

    if st.button("🚀 Run Docking"):

        os.makedirs("work", exist_ok=True)

        # =============================================
        # SAVE PROTEIN
        # =============================================

        with open(protein_path, "rb") as src:

            protein_data = src.read()

        with open("work/protein.pdb", "wb") as dst:

            dst.write(protein_data)

        # =============================================
        # LIGAND
        # =============================================

        if ligand_mode == "Upload":

            if ligand_file is None:

                st.error("Upload ligand first")

                st.stop()

            # =========================================
            # SMI
            # =========================================

            if ligand_file.name.endswith(".smi"):

                with open(
                    "work/ligand.smi",
                    "wb"
                ) as f:

                    f.write(ligand_file.read())

                out, err = run_command(
                    "obabel work/ligand.smi "
                    "-O work/ligand.pdbqt "
                    "--gen3d"
                )

            # =========================================
            # PDBQT
            # =========================================

            else:

                with open(
                    "work/ligand.pdbqt",
                    "wb"
                ) as f:

                    f.write(ligand_file.read())

        # =============================================
        # DATABASE LIGAND
        # =============================================

        else:

            if smiles is None:

                st.error("No ligand selected")

                st.stop()

            with open("work/ligand.smi", "w") as f:

                f.write(smiles)

            out, err = run_command(
                "obabel work/ligand.smi "
                "-O work/ligand.pdbqt "
                "--gen3d"
            )

        # =============================================
        # CHECK LIGAND
        # =============================================

        if not os.path.exists(
            "work/ligand.pdbqt"
        ):

            st.error("Ligand conversion failed")

            st.text(err)

            st.stop()

        # =============================================
        # FAST PROTEIN LOAD
        # =============================================

        st.info("Loading protein...")

        protein_pdbqt = protein_path.replace(
            ".pdb",
            ".pdbqt"
        )

        if not os.path.exists(protein_pdbqt):

            st.error(
                f"PDBQT not found: {protein_pdbqt}"
            )

            st.stop()

        shutil.copy(
            protein_pdbqt,
            "work/protein.pdbqt"
        )

        # =============================================
        # AUTO GRID
        # =============================================

        if grid_mode == "Auto":

            pname = selected_protein.upper()

            found = False

            for key in protein_grids:

                if key in pname:

                    cx, cy, cz = protein_grids[key]

                    sx = sy = sz = 20

                    st.success(f"Auto grid: {key}")

                    found = True

                    break

            if not found:

                st.warning(
                    "Unknown protein → default grid"
                )

                cx = cy = cz = 0

                sx = sy = sz = 20

        # =============================================
        # DOCKING
        # =============================================

        st.info("Running docking...")

        vina_cmd = f"""
        vina --receptor work/protein.pdbqt \
             --ligand work/ligand.pdbqt \
             --center_x {cx} \
             --center_y {cy} \
             --center_z {cz} \
             --size_x {sx} \
             --size_y {sy} \
             --size_z {sz} \
             --cpu 1 \
             --exhaustiveness 4 \
             --out work/result.pdbqt
        """

        out, err = run_command(vina_cmd)

        # =============================================
        # CHECK RESULT
        # =============================================

        if not os.path.exists(
            "work/result.pdbqt"
        ):

            st.error("Docking failed")

            st.text(err)

            st.stop()

        # =============================================
        # CONVERT RESULT
        # =============================================

        run_command(
            "obabel work/result.pdbqt "
            "-O work/result.pdb"
        )

        # =============================================
        # SUCCESS
        # =============================================

        st.success("Docking completed!")

        affinity = extract_affinity(
            "work/result.pdbqt"
        )

        if affinity is not None:

            st.metric(
                "Binding Affinity (kcal/mol)",
                affinity
            )

        # =============================================
        # FILES
        # =============================================

        st.write(
            "📂 Files in work folder:",
            os.listdir("work")
        )

        # =============================================
        # 3D VIEW
        # =============================================

        st.subheader("🧬 3D Visualization")

        if st.button("Show 3D Structure"):

            show_3d()

        # =============================================
        # LOG
        # =============================================

        with st.expander("📄 Log"):

            st.text(out)

            st.text(err)

        
