import pandas as pd
import os
import subprocess

df = pd.read_csv("ligands.csv")

os.makedirs("ligands", exist_ok=True)

for i, row in df.iterrows():
    name = str(row["compound"]).strip().replace(" ", "_")
    smiles = str(row["smiles"]).strip()

    smi_file = f"ligands/{name}.smi"
    pdbqt_file = f"ligands/{name}.pdbqt"

    # ✅ สำคัญ: ต้องมี newline
    with open(smi_file, "w") as f:
        f.write(smiles + "\n")

    cmd = f"obabel {smi_file} -O {pdbqt_file} --gen3d"

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"❌ ERROR: {name}")
        print(result.stderr)
    else:
        print(f"✅ {name} done")

print("🔥 All ligands converted")

