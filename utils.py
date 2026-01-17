# ==========================================
# Library Imports
# ==========================================
import os
import re
import pandas as pd
import torch
from difflib import SequenceMatcher
# Import library AI hanya jika dibutuhkan (biar file ini gak error kalau library belum install)
try:
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    from sentence_transformers import SentenceTransformer
    import faiss
except ImportError:
    print("Warning: Library AI belum lengkap installed.")

# ==========================================
# Configure Paths
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_RESEP_PATH = os.path.join(BASE_DIR, 'data', 'Indonesian_Food_Recipes.csv')
DATA_NUTRISI_PATH = os.path.join(BASE_DIR, 'data', 'nutrition.csv')
MODEL_ADAPTER_PATH = os.path.join(BASE_DIR, 'models', 'model_chef_siap_pakai')

if not BASE_DIR:
    raise ValueError("BASE_DIR tidak ditemukan. Pastikan struktur folder benar.")
elif not DATA_RESEP_PATH:
    raise ValueError("DATA_RESEP_PATH tidak ditemukan. Pastikan file CSV resep ada di folder data.")
elif not DATA_NUTRISI_PATH:
    raise ValueError("DATA_NUTRISI_PATH tidak ditemukan. Pastikan file CSV nutrisi ada di folder data.")
elif not MODEL_ADAPTER_PATH:
    raise ValueError("MODEL_ADAPTER_PATH tidak ditemukan. Pastikan model ada di folder models.")

# ==========================================
# Global Variables
# ==========================================
model = None
tokenizer = None
embedder = None
index = None
df_rag = None

# ==========================================
# Load Resources Function
# ==========================================
def load_resources():
    """
    Tugas: Memuat Model AI, Vector DB, dan Dataset ke RAM.
    Jalan sekali saja saat server start.
    """
    global model, tokenizer, embedder, index, df_rag

    if model is not None:
        print("Resources sudah termuat sebelumnya.")
        return

    print("--- [UTILS] LOADING RESOURCES... ---")

    # TODO: Masukkan logika loading Pandas CSV disini
    # TODO: Masukkan logika loading FAISS Vector DB disini
    # TODO: Masukkan logika loading Qwen Model + Peft Adapter disini

    print("--- [UTILS] SYSTEM READY! ---")

# ==========================================
# Cleanup Output Function
# ==========================================
def super_clean_output(text):
    """
    Tugas: Membersihkan output AI yang kotor.
    - Hapus 'Note:', 'Tips:', 'hehehe'
    - Fix format bullet point strip '-'
    - Hapus duplikasi kalimat (looping)
    """
    # WIP Logic:
    if not text: return ""

    # 1. Fix Formatting basic
    text = text.replace("--", "\n- ")

    # 2. Logic Filter Trash Text
    # ...
    # NOTE: Ini nanti pakai yang ada di kaggle di copy dan implementasi ke sini

    return text

# ==========================================
# 3. Smart Retrieval Function (RAG + Filtering)
# ==========================================
def retrieve_smart_filter(query, mode="normal"):
    """
    Tugas: Mencari resep di database berdasarkan bahan.
    - query: Input user (misal: 'ayam, tahu')
    - mode: 'normal' (mirip bahan) atau 'diet' (high protein)
    """
    # WIP Logic:
    # 1. Encode query jadi vektor
    # 2. Cari 15 kandidat terdekat via FAISS
    # 3. Filter berdasarkan mode (Diet/Normal)
    # 4. Return string Context untuk prompt

    return "Contoh Context: Resep Ayam Goreng (Placeholder)"

# ==========================================
# 4. FUNGSI GENERATOR UTAMA (CONTROLLER)
# ==========================================
def generate_resep_final(bahan_input, mode="normal"):
    """
    Tugas: Fungsi utama yang dipanggil oleh API.
    Alur: Load Check -> Retrieve -> Prompting -> Generate -> Cleaning
    """
    # 1. Cek Model
    if model is None:
        load_resources()

    # 2. Cari Contekan (Context)
    # context = retrieve_smart_filter(bahan_input, mode)

    # 3. Susun Prompt
    # prompt = f"Buat resep {bahan_input}..."

    # 4. Generate via Model
    # outputs = model.generate(...)
    # raw_text = tokenizer.decode(...)

    # 5. Bersihkan Output
    # final_text = super_clean_output(raw_text)

    return "WIP: Ini adalah hasil generate dummy resep untuk " + bahan_input