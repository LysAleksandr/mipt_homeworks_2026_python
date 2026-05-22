from file_utils import replace_file_attachments
from pathlib import Path

def test_replace_attachment(tmp_path: Path) -> None:
    f = tmp_path / 'test.py'
    f.write_text('print(1/0)')
    text = 'Check error @::' + str(f) + '::'
    new_text, errors = replace_file_attachments(text)
    assert 'print(1/0)' in new_text
    assert not errors

def test_file_too_large(tmp_path: Path) -> None:
    f = tmp_path / 'big.txt'
    f.write_bytes(b'x' * (5 * 1024 * 1024 + 1))
    text = 'Attach @::' + str(f) + '::'
    new_text, errors = replace_file_attachments(text)
    assert len(errors) > 0
    assert 'File too large' in errors[0]

def test_file_not_found() -> None:
    text = 'Missing @::/no/such/file.txt::'
    new_text, errors = replace_file_attachments(text)
    assert len(errors) == 1
    assert 'File not found' in errors[0]
    assert '/no/such/file.txt' in new_text