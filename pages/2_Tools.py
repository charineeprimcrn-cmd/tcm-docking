import streamlit as st

st.title("📖 About Docking")

st.markdown("""
## 🧬 Molecular Docking

Molecular docking predicts how a ligand binds to a protein.

### Key:
- Binding affinity
- Binding pose
- Active site

---

### Tools:
- AutoDock Vina
- PyMOL

---

### Workflow:
1. Prepare protein
2. Prepare ligand
3. Run docking
4. Analyze results
""")

st.markdown("---")

st.subheader("🚀 Our Tool")

st.link_button(
    "Open Grid Tool",
    "https://pbd-smartgit-8v3db69d5yajgjhoxff3si.streamlit.app"
)
