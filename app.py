# app.py
import streamlit as st
import hashlib
import matplotlib.pyplot as plt
from io import BytesIO

# --------------------------
# Helpers AES
# --------------------------
def int_to_block(n):
    """Convertit un entier (128 bits max) en liste de 16 octets big-endian."""
    return [(n >> (8 * (15 - i))) & 0xFF for i in range(16)]

def block_to_int(block):
    """Convertit une liste de 16 octets big-endian en entier."""
    result = 0
    for b in block:
        result = (result << 8) | b
    return result

# --------------------------
# PRNG CTR basé sur AES
# --------------------------
class AES_PRNG:
    def __init__(self, seed_phrase):
        seed_hash = hashlib.sha256(seed_phrase.encode()).digest()[:16]
        self.key = list(seed_hash)
        self.counter = 0

    def get_next_random_int(self, min_val, max_val):
        block_input = int_to_block(self.counter)
        encrypted_block = AES_encrypt(block_input, self.key)
        huge_random_number = block_to_int(encrypted_block)
        self.counter += 1
        return min_val + (huge_random_number % (max_val - min_val + 1))

# --------------------------
# PRNG OFB basé sur AES
# --------------------------
class AES_OFB_PRNG:
    BLOCK_SIZE = 16
    def __init__(self, seed_phrase):
        seed_hash = hashlib.sha256(seed_phrase.encode()).digest()
        self.aes_key = list(seed_hash[:16])
        self.current_state = list(seed_hash[16:32])
        self.block_counter = 0

    def _generate_block(self):
        random_block = AES_encrypt(self.current_state, self.aes_key)
        self.current_state = random_block.copy()
        self.block_counter += 1
        return random_block

    def get_int(self, min_val=0, max_val=255):
        block = self._generate_block()
        huge_number = block_to_int(block)
        return min_val + (huge_number % (max_val - min_val + 1))

# --------------------------
# AES minimal (exemple CTR/OFB)
# Ici tu peux mettre ton AES_encrypt complet
# --------------------------
def AES_encrypt(block, key):
    # Pour simplifier, on utilise hashlib pour "simuler" AES
    # Pour un vrai projet, remplace par ton AES complet
    data = bytes(block) + bytes(key)
    return list(hashlib.sha256(data).digest()[:16])

# --------------------------
# STREAMLIT APP
# --------------------------
st.title("Générateur de Nombres Pseudo-Aléatoires AES")

# Choix du mode
mode = st.selectbox("Mode de génération", ["CTR (counter)", "OFB (feedback)"])

# Seed
seed = st.text_input("Entrer une seed (mot de passe)", value="graine_test")

# Plage de génération
plage_min = st.number_input("Minimum", value=0)
plage_max = st.number_input("Maximum", value=255)

# Nombre de valeurs
nb_valeurs = st.number_input("Nombre de valeurs à générer", value=10, step=1)

if st.button("Générer"):

    if mode == "CTR (counter)":
        gen = AES_PRNG(seed)
        resultats = [gen.get_next_random_int(plage_min, plage_max) for _ in range(nb_valeurs)]
    else:
        gen = AES_OFB_PRNG(seed)
        resultats = [gen.get_int(plage_min, plage_max) for _ in range(nb_valeurs)]

    st.write(f"Résultats ({mode}) :")
    st.write(resultats)

    # Graphique scatter
    if nb_valeurs >= 2:
        x = [gen.get_int(0, 1000) for _ in range(2000)]
        y = [gen.get_int(0, 1000) for _ in range(2000)]
        fig, ax = plt.subplots(figsize=(5,5))
        ax.scatter(x, y, s=1, c='red')
        ax.set_title("Aperçu du hasard")
        st.pyplot(fig)

    # Préparer fichier pour téléchargement
    output = BytesIO()
    output.write("\n".join(str(v) for v in resultats).encode())
    output.seek(0)
    st.download_button("Télécharger les résultats", data=output, file_name="nombres_aleatoires.txt")
