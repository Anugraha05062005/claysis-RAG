import os
import sys
import subprocess
import time
import webbrowser
import urllib.request
import threading


# =========================
# OLLAMA CHECK (FIXED)
# =========================
def check_ollama():
    """Verify if Ollama local server is running."""
    print("Checking Ollama status...")

    try:
        req = urllib.request.Request("http://localhost:11434/api/tags")
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                print("[+] Ollama is running successfully.")
                return True
    except Exception:
        pass

    print("[!] Ollama NOT running or not reachable.")
    print("    Please start it using: ollama serve")
    return False


# =========================
# WAIT FOR OLLAMA READY
# =========================
def wait_for_ollama(max_retries=10):
    """Wait until Ollama is fully ready before starting app."""
    print("[*] Waiting for Ollama to be ready...")

    for i in range(max_retries):
        try:
            urllib.request.urlopen(
                "http://localhost:11434/api/tags",
                timeout=3
            )
            print("[+] Ollama is ready!")
            return True
        except Exception:
            print(f"   retry {i+1}/{max_retries}...")
            time.sleep(2)

    print("[!] Ollama not ready after waiting.")
    print("    App will continue, but LLM may fail.")
    return False


# =========================
# MAIN BOOTSTRAP
# =========================
def bootstrap():
    """Build venv if needed and start the application."""

    print("==================================================")
    print(" Starting MoniRAG - Multi-Modal RAG Chatbot Server ")
    print("==================================================")

    # -------------------------
    # 1. Virtual Environment
    # -------------------------
    venv_dir = "venv"
    pip_path = os.path.join(venv_dir, "Scripts", "pip.exe")
    python_path = os.path.join(venv_dir, "Scripts", "python.exe")

    if not os.path.exists(venv_dir):
        print(f"[*] Virtual environment '{venv_dir}' not found. Creating it...")
        subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)
        print("[+] Virtual environment created.")

    # fallback for Linux/Mac
    if not os.path.exists(pip_path):
        pip_path = os.path.join(venv_dir, "bin", "pip")
        python_path = os.path.join(venv_dir, "bin", "python")

    # -------------------------
    # 2. Install Dependencies
    # -------------------------
    print("[*] Installing/Verifying dependencies...")

    try:
        subprocess.run(
            [pip_path, "install", "-r", "requirements.txt"],
            check=True
        )
        print("[+] Dependencies installed successfully.")
    except Exception as e:
        print(f"[-] Dependency installation failed: {e}")
        sys.exit(1)

    # -------------------------
    # 3. Check Ollama
    # -------------------------
    ollama_ok = check_ollama()
    wait_for_ollama()

    # -------------------------
    # 4. Browser Launcher
    # -------------------------
    def open_browser():
        time.sleep(3)
        print("[*] Opening browser...")
        webbrowser.open("http://127.0.0.1:8000")

    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()

    # -------------------------
    # 5. Start FastAPI Server
    # -------------------------
    print("[*] Starting FastAPI server at http://127.0.0.1:8000 ...")

    if not ollama_ok:
        print("[!] WARNING: Ollama not detected. Groq fallback will be used.")

    try:
        cmd = [
            python_path,
            "-m",
            "uvicorn",
            "backend.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8000",
            "--reload"
        ]

        subprocess.run(cmd)

    except KeyboardInterrupt:
        print("\n[+] Server stopped safely.")
    except Exception as e:
        print(f"[-] Server failed: {e}")


# =========================
# ENTRY POINT
# =========================
if __name__ == "__main__":
    bootstrap()