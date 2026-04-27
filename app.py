import streamlit as st
from drbg import AES_DRBG

st.set_page_config(page_title="AES-DRBG Simulator", layout="centered")

if "drbg" not in st.session_state:
    st.session_state.drbg = AES_DRBG()

if "history" not in st.session_state:
    st.session_state.history = []

drbg = st.session_state.drbg

st.title("🚗🔐 AES-DRBG Simulator (ECU-style)")

st.subheader("📡 System State")
st.write(f"Counter V: {drbg.V}")
st.write(f"Reseed counter: {drbg.reseed_counter}")
st.code(drbg.UID.hex())

st.divider()

col1, col2, col3 = st.columns(3)

if col1.button("🎲 Generate"):
    value = drbg.generate(8).hex()
    st.session_state.history.append(value)
    st.success(value)

if col2.button("🔁 Reseed"):
    drbg.reseed()
    st.warning("System reseeded")

if col3.button("🧹 Clear"):
    st.session_state.history = []

st.divider()

st.subheader("📜 History")
for i, v in enumerate(reversed(st.session_state.history), 1):
    st.code(f"{i}. {v}")
