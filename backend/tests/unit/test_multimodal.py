from app.domain.multimodal import kind_from_mime, sanitize_filename, sha256_bytes

def test_kind():
    assert kind_from_mime("image/jpeg")=="image"
    assert kind_from_mime("audio/webm")=="audio"
    assert kind_from_mime("text/csv")=="csv"

def test_sanitize():
    assert sanitize_filename("../../etc/passwd")=="passwd"
    assert sanitize_filename("my file.jpg")=="my_file.jpg"

def test_sha():
    assert len(sha256_bytes(b"hello"))==64
