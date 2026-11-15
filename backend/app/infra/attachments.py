import os, pathlib
from PIL import Image
import io
from ..domain.multimodal import ALLOWED_MIME, MAX_SIZE, kind_from_mime, sanitize_filename, sha256_bytes, sniff_mime
from ..config import settings

def validate_and_store(filename: str, content_type: str, data: bytes, visit_id: int) -> dict:
    if len(data) > MAX_SIZE:
        raise ValueError(f"File too large: {len(data)} > {MAX_SIZE}")
    mime = content_type.split(";")[0].strip().lower()
    kind = kind_from_mime(mime)
    if kind == "unknown":
        # try sniff
        sniffed = sniff_mime(data[:10])
        if sniffed and sniffed in ALLOWED_MIME:
            mime = sniffed
            kind = kind_from_mime(mime)
        else:
            raise ValueError(f"MIME not allowed: {mime}")
    sha = sha256_bytes(data)
    safe_name = sanitize_filename(filename)
    base = pathlib.Path(settings.storage_path).resolve() / str(visit_id)
    base.mkdir(parents=True, exist_ok=True)
    stored_path = base / f"{sha}_{safe_name}"
    # dedup: if exists, don't overwrite
    if not stored_path.exists():
        stored_path.write_bytes(data)
    thumb_path = None
    if kind == "image":
        try:
            img = Image.open(io.BytesIO(data))
            img.thumbnail((320,320))
            thumb_path = base / f"{sha}_thumb.jpg"
            if not thumb_path.exists():
                # strip EXIF by re-saving
                if img.mode in ("RGBA","P"):
                    img = img.convert("RGB")
                img.save(thumb_path, "JPEG", quality=80)
            thumb_path = str(thumb_path)
        except Exception:
            thumb_path = None
    # audio duration stub: len/16000 approximation
    return {
        "kind": kind,
        "mime": mime,
        "size": len(data),
        "sha256": sha,
        "stored_path": str(stored_path),
        "thumb_path": thumb_path,
        "filename": safe_name
    }
