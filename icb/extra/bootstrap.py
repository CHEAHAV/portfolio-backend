import os
import sys
import subprocess


def _run(cmd: list[str], label: str):
    import typer
    typer.echo(f"\n▶  {label}")
    typer.echo(f"   $ {' '.join(cmd)}\n")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        typer.echo(f"\n[error] '{label}' failed with exit code {result.returncode}", err=True)
        raise SystemExit(result.returncode)


def run(
    requirements: str = "requirements.txt",
    host: str = "127.0.0.1",
    port: int = 8000,
    reload: bool = True,
    skip_install: bool = False,
    skip_model: bool = False,
    skip_migrate: bool = False,
):
    import typer

    python = sys.executable

    # ── Step 1: Create requirements.txt if missing ─────────────────────────────
    if not skip_install:
        if not os.path.exists(requirements):
            typer.echo(f"⚠  '{requirements}' not found — creating template...")
            with open(requirements, "w", encoding="utf-8") as f:
                f.write(_requirements_template())
            typer.echo(f"  --> {os.path.abspath(requirements)}")
            typer.echo(f"✅ '{requirements}' created!\n")
        else:
            typer.echo(f"✅ '{requirements}' already exists, skipping.\n")

        # ── Step 2: Install requirements ──────────────────────────────────────
        _run(
            [python, "-m", "pip", "install", "-r", requirements],
            f"Installing dependencies from {requirements}",
        )
    else:
        typer.echo("⏭  Skipping pip install (--skip-install)")

    # ── Step 3: Create model ───────────────────────────────────────────────────
    if not skip_model:
        _run(
            [python, "-m", "icb", "create-model"],
            "Running icb create-model",
        )
    else:
        typer.echo("⏭  Skipping create-model (--skip-model)")

    # ── Step 4: Migrate ────────────────────────────────────────────────────────
    if not skip_migrate:
        _run(
            [python, "-m", "icb", "migrate"],
            "Running icb migrate",
        )
    else:
        typer.echo("⏭  Skipping migrate (--skip-migrate)")

    # ── Step 5: Start uvicorn ─────────────────────────────────────────────────
    uvicorn_cmd = [
        python, "-m", "uvicorn", "main:app",
        "--host", host,
        "--port", str(port),
    ]
    if reload:
        uvicorn_cmd.append("--reload")

    _run(uvicorn_cmd, f"Starting Uvicorn on {host}:{port}")


# ── Template ──────────────────────────────────────────────────────────────────
# Edit these freely — whatever you write here is what gets generated.

def _requirements_template() -> str:
    return """\
bcrypt==4.0.1
certifi==2026.2.25
cffi==2.0.0
charset-normalizer==3.4.6
click==8.3.1
cryptography==46.0.6
dnspython==2.8.0
ecdsa==0.19.2
email-validator==2.3.0
fastapi==0.135.2
greenlet==3.3.2
h11==0.16.0
httptools==0.7.1
numpy==2.4.4
passlib==1.7.4
Pillow==12.1.1
psycopg2-binary==2.9.11
pyasn1==0.6.3
pycparser==3.0
python-dotenv==1.2.2
python-jose==3.5.0
python-multipart==0.0.22
python-resize-image==1.1.20
PyYAML==6.0.3
requests==2.33.0
rsa==4.9.1
six==1.17.0
sniffio==1.3.1
SQLAlchemy==2.0.48
urllib3==2.6.3
uvicorn==0.42.0
watchfiles==1.1.1
websockets==16.0
pandas==3.0.1
boto3==1.42.78
fastapi-cache2==0.2.2
redis==7.4.0
Werkzeug==3.1.7
httpx==0.28.1
pytest==9.0.2
openpyxl==3.1.5
weasyprint==68.1
haversine==2.9.0
numerize==0.12
qrcode==8.2
cython==3.2.4
celery==5.6.3
google-auth==2.49.1
firebase-admin==7.3.0
Jinja2==3.1.6
typer==0.24.1
"""