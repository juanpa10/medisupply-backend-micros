import io
import pytest
from werkzeug.datastructures import FileStorage
from app.core.utils.validators import (
    validate_file_extension,
    validate_file_size,
    validate_file_mime_type
)
from app.core.exceptions import FileUploadError


def make_file(filename, content_bytes):
    f = io.BytesIO(content_bytes)
    fs = FileStorage(stream=f, filename=filename)
    return fs


def test_invalid_extension_raises():
    with pytest.raises(FileUploadError):
        validate_file_extension('file.exe', allowed_extensions=['pdf', 'png'])


def test_too_large_raises():
    f = make_file('a.pdf', b'a' * 1024 * 1024 * 6)  # 6MB
    with pytest.raises(FileUploadError):
        validate_file_size(f, max_size=5 * 1024 * 1024)


def test_bad_mime_raises(monkeypatch):
    f = make_file('a.pdf', b'notreallypdf')
    # monkeypatch magic.from_buffer to return an unexpected mime
    monkeypatch.setattr('app.core.utils.validators.magic.from_buffer', lambda b, mime: 'application/x-msdownload')
    with pytest.raises(FileUploadError):
        validate_file_mime_type(f)
