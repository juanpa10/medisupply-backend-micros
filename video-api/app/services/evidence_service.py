import os, mimetypes, time, hmac, hashlib, base64
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Optional, Tuple, Dict, Any
from app.repositories.evidence_repository import EvidenceRepository

# reglas de validación
PHOTO_MAX = 10 * 1024 * 1024      # 10 MB
VIDEO_MAX = 200 * 1024 * 1024     # 200 MB
PHOTO_EXT = {".jpg", ".jpeg", ".png"}
VIDEO_EXT = {".mp4", ".mov"}

@dataclass
class UploadResult:
    id: int
    filename: str
    url: str

class EvidenceService:
    def __init__(self, repo: EvidenceRepository, upload_dir: str, secret_key: str):
        self.repo = repo
        self.upload_dir = upload_dir
        self.secret_key = secret_key.encode("utf-8")
        os.makedirs(self.upload_dir, exist_ok=True)

    def _validate(self, filename: str, size_bytes: int, evidence_type: str) -> Tuple[bool, str]:
        ext = os.path.splitext(filename)[1].lower()
        if evidence_type not in {"photo", "video"}:
            return False, "Tipo de evidencia inválido"
        if evidence_type == "photo":
            if ext not in PHOTO_EXT:
                return False, "Formato de foto no soportado"
            if size_bytes > PHOTO_MAX:
                return False, "Archivo demasiado grande (foto)"
        else:
            if ext not in VIDEO_EXT:
                return False, "Formato de video no soportado"
            if size_bytes > VIDEO_MAX:
                return False, "Archivo demasiado grande (video)"
        return True, ""

    def _sign(self, path: str, expires_in: int = 900) -> str:
        expiry = int(time.time()) + expires_in
        msg = f"{path}:{expiry}".encode("utf-8")
        sig = hmac.new(self.secret_key, msg, hashlib.sha256).digest()
        b64 = base64.urlsafe_b64encode(sig).decode("ascii").rstrip("=")
        return f"/files?path={path}&exp={expiry}&sig={b64}"

    def save_upload(self, stream, filename: str, size_bytes: int, meta: Dict[str, Any]) -> UploadResult:
        ok, err = self._validate(filename, size_bytes, meta.get("evidence_type"))
        if not ok:
            raise ValueError(err)

        # almacenar
        ts = datetime.utcnow().strftime("%Y%m%dT%H%M%S%fZ")
        safe_name = f"{ts}_{os.path.basename(filename)}"
        stored_path = os.path.join(self.upload_dir, safe_name)
        with open(stored_path, "wb") as f:
            f.write(stream.read())

        rec = self.repo.create(
            filename=safe_name,
            content_type=meta.get("content_type") or "",
            size_bytes=size_bytes,
            client_id=str(meta.get("client_id")),
            product_id=str(meta.get("product_id")),
            visit_id=str(meta.get("visit_id")),
            user=meta.get("user"),
            evidence_type=meta.get("evidence_type"),
            lat=meta.get("lat"),
            lon=meta.get("lon"),
            stored_path=stored_path,
        )
        url = self._sign(safe_name, 900)
        return UploadResult(id=rec.id, filename=safe_name, url=url)

    def signed_url_for(self, filename: str, expires_in: int = 900) -> str:
        return self._sign(filename, expires_in)
