import streamlit as st
import hashlib
from copy import deepcopy
from functools import lru_cache
import matplotlib.pyplot as plt

# --------------------------
# AES helpers (ton code existant)
# --------------------------

# ... (copie ici tout ton code AES, int_to_block, block_to_int, AES_encrypt, AES_decrypt, etc.) ...

# --------------------------
# PRNG basés sur AES
# --------------------------

class AES_PRNG:
    """PRNG simple basé sur AES-CTR avec seed_phrase"""
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


class AES_OFB_PRNG:
    """PRNG AES-128 en mode OFB basé sur seed_phrase"""
    BLOCK_SIZE = 16

    def __init__(self, seed_phrase):
        seed_hash = hashlib.sha256(seed_phrase.encode()).digest()
        self.aes_key = list(seed_hash[:16])
        self.current_state = list(seed_hash[16:32])
        self.block_counter = 0

    def _generate_block(self):
        block = AES_encrypt(self.current_state, self.aes_key)
        self.current_state = block.copy()
        self.block_counter += 1
        return block

    def get_int(self, min_val=0, max_val=255):
        block = self._generate_block()
        huge_number = block_to_int(block)
        return min_val + (huge_number % (max_val - min_val + 1))

    def get_bytes(self, num_bytes):
        output = []
        while len(output) < num_bytes:
            block = self._generate_block()
            remaining = num_bytes - len(output)
            output.extend(block[:remaining] if remaining < self.BLOCK_SIZE else block)
        return output

    def get_hex(self, num_bytes):
        return ''.join(f"{b:02x}" for b in self.get_bytes(num_bytes))


# --------------------------
# Streamlit UI
# --------------------------

st.set_page_config(page_title="AES PRNG Demo", layout="wide")
st.title("Générateur de nombres pseudo-aléatoires AES")

mode = st.sidebar.radio("Choisir le mode PRNG :", ["AES-CTR Seed", "AES-OFB Seed"])

seed_phrase = st.text_input("Entrez votre seed phrase :", value="graine_de_test_2CS")
nb_valeurs = st.number_input("Nombre de valeurs à générer :", min_value=1, max_value=10000, value=10)
plage_min = st.number_input("Valeur minimale :", value=0)
plage_max = st.number_input("Valeur maximale :", value=255)

if st.button("Générer"):

    if mode == "AES-CTR Seed":
        gen = AES_PRNG(seed_phrase)
    else:
        gen = AES_OFB_PRNG(seed_phrase)

    resultats = [gen.get_next_random_int(plage_min, plage_max) for _ in range(nb_valeurs)]
    st.write("### Résultats :", resultats)

    # Graphique rapide
    plt.figure(figsize=(6,4))
    plt.hist(resultats, bins=20, color='skyblue', edgecolor='black')
    plt.title("Distribution des nombres générés")
    plt.xlabel("Valeurs")
    plt.ylabel("Fréquence")
    st.pyplot(plt)

    # Option hex si OFB
    if mode == "AES-OFB Seed":
        st.write("### 5 blocs hex générés :")
        blocs_hex = [gen.get_hex(16) for _ in range(5)]
        st.write(blocs_hex)
