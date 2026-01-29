from waitress import serve
from app import app

# This for Production using Tailscale Funnel
if __name__ == "__main__":
    print("Server is running on http://localhost:5000")
    serve(app, host='0.0.0.0', port=5000, threads=3)