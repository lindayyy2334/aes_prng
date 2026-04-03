import streamlit as st
import hashlib
import matplotlib.pyplot as plt
from io import BytesIO

# --------------------------
# Helpers
# --------------------------
def int_to_block(n):
    return [(n >> (8 * (15 - i))) & 0xFF for i in range(16)]

def block_to_int(block):
    result = 0
    for b in block:
        result = (result << 8) | b
    return result

def AES_encrypt(block, key):
    # Simulation AES (remplace par ton AES complet si besoin)
    data = bytes(block) + bytes(key)
    return list(hashlib.sha256(data).digest()[:16])

# --------------------------
# PRNG CTR
# --------------------------
class AES_PRNG:
    def __init__(self, seed):
        seed_hash = hashlib.sha256(seed.encode()).digest()[:16]
        self.key = list(seed_hash)
        self.counter = 0

    def get_int(self, min_val, max_val):
        block = int_to_block(self.counter)
        enc = AES_encrypt(block, self.key)
        num = block_to_int(enc)
        self.counter += 1
        return min_val + (num % (max_val - min_val + 1))

# --------------------------
# PRNG OFB
# --------------------------
class AES_OFB_PRNG:
    def __init__(self, seed):
        seed_hash = hashlib.sha256(seed.encode()).digest()
        self.key = list(seed_hash[:16])
        self.state = list(seed_hash[16:32])

    def _next_block(self):
        block = AES_encrypt(self.state, self.key)
        self.state = block.copy()
        return block

    def get_int(self, min_val, max_val):
        block = self._next_block()
        num = block_to_int(block)
        return min_val + (num % (max_val - min_val + 1))

# --------------------------
# UI
# --------------------------
st.set_page_config(layout="wide")
st.title("🔐 AES PRNG Visual Lab")

st.sidebar.header("⚙️ Configuration")

seed = st.sidebar.text_input("Seed", "graine_test")
n = st.sidebar.slider("Nombre de valeurs", 10, 5000, 500)
min_val = st.sidebar.number_input("Min", value=0)
max_val = st.sidebar.number_input("Max", value=255)

generate = st.sidebar.button("🚀 Générer")

if generate:

    ctr = AES_PRNG(seed)
    ofb = AES_OFB_PRNG(seed)

    ctr_vals = [ctr.get_int(min_val, max_val) for _ in range(n)]
    ofb_vals = [ofb.get_int(min_val, max_val) for _ in range(n)]

    # --------------------------
    # Affichage
    # --------------------------
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("CTR Mode")
        st.write(ctr_vals[:20])

        fig1, ax1 = plt.subplots()
        ax1.hist(ctr_vals, bins=30)
        ax1.set_title("Distribution CTR")
        st.pyplot(fig1)

    with col2:
        st.subheader("OFB Mode")
        st.write(ofb_vals[:20])

        fig2, ax2 = plt.subplots()
        ax2.hist(ofb_vals, bins=30)
        ax2.set_title("Distribution OFB")
        st.pyplot(fig2)

    # --------------------------
    # Scatter comparaison
    # --------------------------
    st.subheader("Comparaison visuelle (scatter)")
    x = ctr_vals[:1000]
    y = ofb_vals[:1000]

    fig3, ax3 = plt.subplots()
    ax3.scatter(x, y, s=5)
    ax3.set_title("CTR vs OFB")
    st.pyplot(fig3)

    # --------------------------
    # Export
    # --------------------------
    st.subheader("📥 Export des données")

    file_content = "CTR,OFB\n"
    for c, o in zip(ctr_vals, ofb_vals):
        file_content += f"{c},{o}\n"

    st.download_button(
        label="Télécharger CSV",
        data=file_content,
        file_name="prng_data.csv",
        mime="text/csv"
    )
