#!/usr/bin/env python3
"""
2Saisons - Script de demarrage rapide.
Lance l'API et le frontend en local (sans Docker).

Usage :
    python start.py              # API + Frontend
    python start.py --api-only   # API uniquement
    python start.py --frontend-only  # Frontend uniquement
"""
import sys, subprocess, os, signal, time, shutil

API_PORT = 8000
FRONTEND_PORT = 8080

def start_api():
    """Lance le backend FastAPI."""
    os.chdir(os.path.join(os.path.dirname(__file__), "backend"))
    print("Demarrage de l'API 2Saisons...")
    subprocess.run([sys.executable, "seed.py"], check=False)
    return subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0",
         "--port", str(API_PORT), "--reload"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )

def start_frontend():
    """Lance le frontend Vue/Vite."""
    os.chdir(os.path.join(os.path.dirname(__file__), "frontend-vue"))
    npm = "npm.cmd" if os.name == "nt" else "npm"
    if not shutil.which(npm):
        raise RuntimeError("Node.js et npm sont requis pour lancer le frontend Vue.")
    print("Demarrage du Frontend Vue...")
    return subprocess.Popen(
        [npm, "run", "dev", "--", "--host", "0.0.0.0", "--port", str(FRONTEND_PORT)],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    processes = []

    # Installation des dependances backend
    print("Installation des dependances backend...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-r", "backend/requirements.txt"])

    args = set(sys.argv[1:])

    if not args or "--api-only" in args:
        p = start_api()
        processes.append(("API", p))

    if not args or "--frontend-only" in args:
        # Attendre que l'API soit prete
        if any("API" in n for n, _ in processes) or not args:
            print("Attente de l'API...")
            time.sleep(3)
        p = start_frontend()
        processes.append(("Frontend", p))

    if processes:
        print("\n" + "=" * 50)
        print("2Saisons - Application demarree !")
        print("=" * 50)
        for name, p in processes:
            print(f"   {name} : PID {p.pid}")
        print(f"\n   API Swagger  : http://localhost:{API_PORT}/docs")
        print(f"   Frontend     : http://localhost:{FRONTEND_PORT}")
        print(f"   Health       : http://localhost:{API_PORT}/health")
        print("\n   Ctrl+C pour arreter.\n" + "=" * 50)

        try:
            while processes:
                for i, (name, p) in enumerate(processes):
                    if p.poll() is not None:
                        print(f"[{name}] Termine avec code {p.returncode}")
                        processes.pop(i)
                        break
                    # Lire la sortie de chaque processus
                    line = p.stdout.readline()
                    if line:
                        print(f"[{name}] {line.decode('utf-8', errors='replace').rstrip()}")
                if not processes:
                    break
        except KeyboardInterrupt:
            print("\nArret...")
            for name, p in processes:
                p.terminate()
                p.wait()
            print("Arrete.")
