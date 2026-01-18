# ==========================================
# Library Imports
# ==========================================
import os
import re
import pandas as pd
import torch
from difflib import SequenceMatcher
from functools import wraps
from flask import request, jsonify, session

try:
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, TextStreamer
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

# Validasi Path (Safety Check)
if not BASE_DIR:
    raise ValueError("BASE_DIR tidak ditemukan.")
elif not DATA_RESEP_PATH:
    raise ValueError("DATA_RESEP_PATH tidak ditemukan.")
elif not DATA_NUTRISI_PATH:
    raise ValueError("DATA_NUTRISI_PATH tidak ditemukan.")
elif not MODEL_ADAPTER_PATH:
    raise ValueError("MODEL_ADAPTER_PATH tidak ditemukan.")

# ==========================================
# Global Variables
# ==========================================
model = None
tokenizer = None
embedder = None
index = None
df_rag = None

# ==========================================
# Helper: Similarity Check (Anti-Looping)
# ==========================================
def similar(a, b):
    """Mengecek kemiripan dua kalimat (0.0 - 1.0)"""
    return SequenceMatcher(None, a, b).ratio()

# ==========================================
# 1. Load Resources Function
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

    # A. LOAD DATASET & MERGE NUTRISI
    print("   [1/3] Loading Dataset & Nutrisi...")
    try:
        df_resep = pd.read_csv(DATA_RESEP_PATH)
        try:
            df_nutri = pd.read_csv(DATA_NUTRISI_PATH)
            # Normalisasi
            df_resep['temp_key'] = df_resep['Title'].str.lower().str.strip()
            df_nutri['temp_key'] = df_nutri['name'].str.lower().str.strip()
            # Merge
            df_full = df_resep.merge(df_nutri[['temp_key', 'calories', 'proteins']], on='temp_key', how='left')
            df_full[['calories', 'proteins']] = df_full[['calories', 'proteins']].fillna(-1)
            df_full.drop(columns=['temp_key'], inplace=True)
        except Exception as e:
            print(f"   [WARN] Gagal merge nutrisi ({e}). Lanjut tanpa nutrisi.")
            df_full = df_resep
            df_full['calories'] = -1
            df_full['proteins'] = -1

        df_rag = df_full.copy()
        # Clean Ingredients buat search
        df_rag['Ingredients_Clean'] = df_rag['Ingredients'].astype(str).str.replace('--', ' ')
        df_rag['search_text'] = "Masakan: " + df_rag['Title'] + " Bahan: " + df_rag['Ingredients_Clean']

    except Exception as e:
        print(f"   [FATAL] Gagal load dataset: {e}")
        return

    # B. BUILD VECTOR DB (FAISS)
    print("   [2/3] Building Vector Database (FAISS)...")
    try:
        embedder = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        embeddings = embedder.encode(df_rag['search_text'].tolist(), show_progress_bar=True)
        index = faiss.IndexFlatL2(embeddings.shape[1])
        index.add(embeddings)
    except Exception as e:
        print(f"   [FATAL] Gagal build FAISS: {e}")
        return

    # C. LOAD AI MODEL (Qwen + Adapter)
    print("   [3/3] Loading AI Model (Qwen 1.5B)...")
    try:
        base_model_name = "Qwen/Qwen2-1.5B-Instruct"

        # Lower memory usage with 4-bit quantization
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
        )

        base_model = AutoModelForCausalLM.from_pretrained(
            base_model_name,
            # torch_dtype=torch.float16,
            quantization_config=bnb_config,
            device_map="auto",
            trust_remote_code=True
        )
        model = PeftModel.from_pretrained(base_model, MODEL_ADAPTER_PATH)
        tokenizer = AutoTokenizer.from_pretrained(base_model_name, trust_remote_code=True)
        model.eval()
    except Exception as e:
        print(f"   [FATAL] Gagal load AI Model: {e}")
        return

    print("--- [UTILS] SYSTEM READY! Semua resource siap. ---")


# ==========================================
# 2. Cleanup Output Function (Nuclear)
# ==========================================
def super_clean_output(text):
    """
    Tugas: Membersihkan output AI (Anti-Loop, Format Fix, Kill Switch).
    """
    if not text: return ""

    # Pre-processing
    text = text.replace("--", "\n- ")
    text = text.replace("Bahan-bahan Lengkap:", "Bahan-bahan:")
    text = re.sub(r',(?!\s|\d)', ', ', text) # Fix spasi koma

    lines = text.split('\n')
    cleaned_lines = []

    section = "HEADER"
    seen_lines = []

    # Kill Switch Phrases
    kill_switch = [
        "Tips:", "Tips :", "Note:", "Note :", "Catatan:", "P.S.",
        "Selamat mencoba", "Happy cooking", "Semoga bermanfaat",
        "Untuk mengetahui nutrisinya", "Data nutrisi ini",
        "Kalau mau disajikan", "Sajikan hangat"
    ]

    for line in lines:
        stripped = line.strip()

        # Skip baris kosong/strip doang
        if not stripped or stripped in ["-", "- "]:
            if not stripped and cleaned_lines and cleaned_lines[-1]: cleaned_lines.append("")
            continue

        # Stop jika ketemu kata terlarang
        if any(k in stripped for k in kill_switch): break

        # Anti-Looping Logic
        is_looping = False
        for seen in seen_lines[-5:]:
            if similar(stripped, seen) > 0.85 and len(stripped) > 10:
                is_looping = True
                break
        if is_looping: continue

        # Deteksi Section
        if "Bahan-bahan:" in stripped or "Bahan:" in stripped:
            section = "BAHAN"
            cleaned_lines.append("\nBahan-bahan:")
            continue
        elif "Cara Membuat:" in stripped or "Langkah:" in stripped:
            section = "CARA"
            cleaned_lines.append("\nCara Membuat:")
            continue
        elif "Informasi Gizi" in stripped or "Info Nutrisi" in stripped:
            section = "GIZI"
            cleaned_lines.append("\nInformasi Gizi (Estimasi per porsi):")
            continue

        # Formatting per Section
        if section == "BAHAN":
            if stripped.startswith("-"):
                cleaned_lines.append(stripped)
            elif stripped[0].isdigit() or stripped[0].isalpha():
                cleaned_lines.append(f"- {stripped}")
        elif section == "CARA":
            cleaned_lines.append(stripped)
        elif section == "GIZI":
            valid_keys = ["kalori", "protein", "karbo", "lemak", "kcal", "gram", "g="]
            if any(k in stripped.lower() for k in valid_keys):
                cleaned_lines.append(stripped)
        else:
            if "Nama Masakan:" in stripped: cleaned_lines.append(stripped)

        seen_lines.append(stripped)

    # Fallback Nutrisi
    result = '\n'.join(cleaned_lines).strip()
    if "Informasi Gizi" in result:
        last_lines = result.split("Informasi Gizi")[-1]
        if len(last_lines.strip()) < 5:
            result += "\n- Kalori: Estimasi 350-500 kkal\n- Protein: Data spesifik belum tersedia"
    else:
        result += "\n\nInformasi Gizi (Estimasi per porsi):\n- Kalori: Estimasi 350-500 kkal\n- Protein: Data spesifik belum tersedia"

    return result


# ==========================================
# 3. Smart Retrieval Function
# ==========================================
def retrieve_smart_filter(query, mode="normal"):
    """
    Tugas: Mencari resep (RAG) dengan filter Normal/Diet.
    """
    if index is None or df_rag is None:
        print("[ERR] Resources belum dimuat!")
        return None

    print(f"--- [RAG] Searching for: '{query}' (Mode: {mode}) ---")

    # Encode & Search
    query_vector = embedder.encode([query])
    distances, indices = index.search(query_vector, 15)

    candidates = []
    for i in range(15):
        idx = indices[0][i]
        if idx == -1: continue
        row = df_rag.iloc[idx].copy()
        candidates.append(row)

    if not candidates: return None

    # Logic Filter
    best_item = candidates[0]
    if mode == "diet":
        valid_candidates = [c for c in candidates if c['proteins'] > 0]
        if valid_candidates:
            valid_candidates.sort(key=lambda x: x['proteins'], reverse=True)
            best_item = valid_candidates[0]
            print(f"   [FILTER] Mode Diet: {best_item['Title']} ({best_item['proteins']}g Protein)")

    # Prepare Context
    nutri_str = "Data tidak tersedia"
    if best_item['calories'] != -1:
        nutri_str = f"Kalori: {best_item['calories']} kcal, Protein: {best_item['proteins']} g"

    return (f"Judul: {best_item['Title']}\n"
            f"Bahan Asli: {best_item['Ingredients']}\n"
            f"Langkah Asli: {best_item['Steps']}\n"
            f"[Info Nutrisi Dataset]: {nutri_str}")


# ==========================================
# 4. Main Generator (Controller)
# ==========================================
def generate_resep_final(bahan_input, mode="normal"):
    """
    Tugas: Pipeline Utama (Load -> Retrieve -> Generate -> Clean).
    """
    if model is None: load_resources()

    # 1. Retrieve
    context = retrieve_smart_filter(bahan_input, mode)
    if context is None:
        return f"Maaf, stok resep untuk '{bahan_input}' tidak ditemukan."

    # 2. Prompt Engineering
    diet_instruction = ""
    if mode == "diet":
        diet_instruction = "Karena user meminta MODE DIET, kurangi penggunaan minyak, gula, dan santan."

    prompt = f"""### Instruction:
Anda adalah Chef Profesional. Buat SATU resep lengkap menggunakan bahan '{bahan_input}' berdasarkan referensi [CONTEXT] berikut.

ATURAN PENTING:
1. Format Output WAJIB:
   - Nama Masakan: [Nama yang menarik]
   - Bahan-bahan: [List bahan dengan bullet point]
   - Cara Membuat: [Langkah-langkah dengan nomor]
   - Informasi Gizi: [Estimasi Kalori & Protein]
2. Gunakan Bahasa Indonesia yang rapi.
3. JANGAN mengulang-ulang kalimat.
4. {diet_instruction}

[CONTEXT]:
{context}

### Input:
Buatkan resep untuk: {bahan_input}

### Response:
"""

    # 3. Generate
    print("--- [AI] Generating Recipe... ---")
    try:
        streamer = TextStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)

        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        with torch.no_grad():
            outputs = model.generate(
                **inputs, max_new_tokens=700,
                temperature=0.3,
                repetition_penalty=1.2,
                do_sample=True,
                eos_token_id=tokenizer.eos_token_id,
                pad_token_id=tokenizer.pad_token_id,
                streamer=streamer
            )

        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        raw_output = response.split("### Response:")[-1].strip() if "### Response:" in response else response

    except Exception as e:
        print(f"[ERR] Error Generate: {e}")
        return "Maaf, dapur sedang kendala teknis."

    # 4. Clean & Return
    return super_clean_output(raw_output)

# ==========================================
# Helper: Validation Functions
# ==========================================
def email_format(email):
    """
    Tugas: Validasi format email sederhana menggunakan Regex.
    """
    if not email: return False
    # Pattern standar email
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def minimum_password(password):
    """
    Tugas: Validasi kekuatan password.
    Aturan: Minimal 8 karakter, ada huruf besar, huruf kecil, angka, dan simbol.
    """
    if not password: return False
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password): # Huruf Besar
        return False
    if not re.search(r'[a-z]', password): # Huruf Kecil
        return False
    if not re.search(r'[0-9]', password): # Angka
        return False
    if not re.search(r'[\W_]', password): # Simbol
        return False
    return True

def data_validate():
    """
    Otomatis ambil JSON. Kalau kosong, return error response.
    Cara pakai: data, error = utils.get_json_input()
    """
    data = request.get_json()
    if not data:
        return None, (jsonify({
            'error_code': 400,
            'success': False,
            'message': 'Invalid JSON data.'
        }), 400)

    return data, None

def auth_required(f):
    """
    Decorator: Cek apakah user sudah login (session).
    Cara pakai: @utils.auth_required
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Cek session
        if 'user_id' not in session:
            return jsonify({
                'error_code': 401,
                'success': False,
                'message': 'Authentication required. Please log in.'
            }), 401
        return f(*args, **kwargs)
    return decorated_function
