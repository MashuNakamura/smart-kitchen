# 🍳 SmartKitchen AI

**Intelligent Recipe Generator Based on Available Ingredients using Hybrid RAG & Local LLM**

SmartKitchen AI adalah aplikasi "Virtual Chef" yang dirancang untuk mengatasi masalah Decision Fatigue (bingung mau masak apa) dan Food Waste pada mahasiswa/anak kos. Aplikasi ini menggunakan kecerdasan buatan untuk menyarankan resep masakan Indonesia berdasarkan stok bahan yang kamu miliki di kulkas, tanpa perlu koneksi internet server yang mahal (Localhost).

## 🌟 Key Features

Berdasarkan validasi user dan pengembangan sistem, berikut fitur unggulan SmartKitchen:
- **🛒 Inventory-Based Cooking**: Masak dari apa yang ada. Input bahan -> Jadi Resep.
- **🧠 Dual Mode Generator**:
    - **Normal Mode**: Fokus pada rasa dan kenyang.
    - **Diet Mode**: Fokus pada rendah kalori dan metode sehat.
- **⚡ Zero-Friction UX**: Hasil instruksi step-by-step langsung tanpa intro blog atau iklan.
- **📥 PDF Export**: Simpan resep hasil generate menjadi PDF siap cetak.
- **🏷️ Smart Ingredient Pool**: Database 50+ bahan lokal untuk akurasi input tinggi.
- **🔒 High Security**: Password Hashing (Bcrypt), Input Sanitization (Anti-Prompt Injection), & Rate Limiting.

## 🏗️ Tech Stack & Architecture

Aplikasi ini menggunakan arsitektur Hybrid Edge Computing untuk performa maksimal dengan biaya nol (Zero Cost Deployment).

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Frontend** | HTML5 + Tailwind CSS | Responsive design (Desktop/Mobile) |
| **Backend** | Python Flask | Lightweight web server |
| **Database** | SQLite | Relational DB for User, History, & Cache |
| **AI Model** | Qwen2-1.5B-Instruct | Int4 Quantization. Dipilih karena ringan (<4GB VRAM) & paham konteks Indonesia. |
| **Logic** | Hybrid RAG | Retrieval-Augmented Generation menggunakan Vector DB (FAISS) untuk mencegah halusinasi. |
| **Deployment** | Tailscale Funnel | Secure Cloud Tunneling untuk akses publik (HTTPS). |

## 🚀 Getting Started

Ikuti langkah berikut untuk menjalankan SmartKitchen di komputer lokal Anda (Windows/Linux/MacOS).

### 1. Prerequisites
Pastikan Anda sudah menginstal:
- **Python 3.10** atau lebih baru
- **Git**

### 2. Setup Project & Environment
Clone repository ini dan masuk ke direktorinya.

**Setup Environment Variables:**
Copy file `.env.example` ke `.env` dan sesuaikan konfigurasinya (opsional untuk deployment sendiri).
```bash
cp .env.example .env
```
*Pastikan SMTP sudah dikonfigurasi di `.env` jika ingin fitur email OTP berjalan.*

### 3. Download Models
Aplikasi ini membutuhkan model AI lokal.
Anda bisa mendownload model yang sudah kami fine-tuning dari link berikut: [Link Models](https://drive.google.com/file/d/1xvsD3ahpbGbT3L5xywdYzfckQzmDIugD/view)
 -> Extract ke folder `models/`.

Setelah itu download base model Qwen dari HuggingFace:

```bash
mkdir -p models/base_model
cd models/base_model

wget "https://huggingface.co/Qwen/Qwen2-1.5B-Instruct/resolve/main/config.json" -O config.json
wget "https://huggingface.co/Qwen/Qwen2-1.5B-Instruct/resolve/main/generation_config.json" -O generation_config.json
wget "https://huggingface.co/Qwen/Qwen2-1.5B-Instruct/resolve/main/tokenizer_config.json" -O tokenizer_config.json
wget "https://huggingface.co/Qwen/Qwen2-1.5B-Instruct/resolve/main/tokenizer.json" -O tokenizer.json
wget "https://huggingface.co/Qwen/Qwen2-1.5B-Instruct/resolve/main/vocab.json" -O vocab.json
wget "https://huggingface.co/Qwen/Qwen2-1.5B-Instruct/resolve/main/merges.txt" -O merges.txt
wget -c "https://huggingface.co/Qwen/Qwen2-1.5B-Instruct/resolve/main/model.safetensors" -O model.safetensors

cd ../../
```

### 4. Database & Dependencies

**Buat folder database:**
```bash
mkdir -p db
```

**Install Dependencies:**
Pastikan `virtualenv` sudah aktif jika Anda menggunakannya (direkomendasikan).
```bash
pip install -r requirements.txt
```

### 5. Running the Application

Jalankan backend AI dan frontend Flask secara terpisah.

#### **Windows**
1.  **Jalankan Model AI Server** (Terminal 1):
    Double click `model.bat` atau jalankan via terminal:
    ```cmd
    .\model.bat
    ```
    *Tunggu sampai muncul "Model Server Ready".*

2.  **Jalankan Web App** (Terminal 2):
    Double click `run.bat` atau jalankan via terminal:
    ```cmd
    .\run.bat
    ```

#### **Linux / MacOS**
1.  **Berikan izin eksekusi script:**
    ```bash
    chmod +x model.sh run.sh
    ```

2.  **Jalankan Model AI Server** (Terminal 1):
    ```bash
    ./model.sh
    ```
    *Tunggu sampai muncul "Model Server Ready".*

3.  **Jalankan Web App** (Terminal 2):
    ```bash
    ./run.sh
    ```

Akses aplikasi di browser melalui: [http://localhost:5000](http://localhost:5000)

---

## 👥 Our Team (Kelompok 3)

- **Federico Matthew Pratama** - AI Architect & Team Lead
- **Jefferey Chealfiro Isdhianto** - Data Scientist & Frontend Engineer
- **Fernando Perry** - MLOps & Infrastructure

---
**SmartKitchen AI - 2026**