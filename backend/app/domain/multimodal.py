import hashlib, os, re

ALLOWED_MIME = {
    "image/jpeg": "image",
    "image/png": "image",
    "audio/webm": "audio",
    "audio/wav": "audio",
    "audio/x-wav": "audio",
    "audio/mpeg": "audio",
    "audio/mp3": "audio",
    "application/pdf": "pdf",
    "text/csv": "csv",
    "text/plain": "csv",
    "application/vnd.ms-excel": "csv",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "csv",
}

MAX_SIZE = 10 * 1024 * 1024

def kind_from_mime(mime: str) -> str:
    return ALLOWED_MIME.get(mime.split(";")[0].strip().lower(), "unknown")

def sanitize_filename(name: str) -> str:
    name = os.path.basename(name)
    name = re.sub(r"[^a-zA-Z0-9._-]", "_", name)
    return name[:120]

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

# Magic byte stubs (deterministic, not full validation)
MAGIC = {
    b"\xff\xd8\xff": "image/jpeg",
    b"\x89PNG": "image/png",
    b"RIFF": "audio/wav",  # simplified
    b"%PDF": "application/pdf",
}

def sniff_mime(head: bytes) -> str | None:
    for k, v in MAGIC.items():
        if head.startswith(k):
            return v
    return None
