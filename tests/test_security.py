from pathlib import Path
from skeletor.security import is_sensitive

def test_is_sensitive_env_files():
    assert is_sensitive(Path(".env"))
    assert is_sensitive(Path(".env.local"))
    assert is_sensitive(Path("prod.env"))
    assert is_sensitive(Path(".envrc"))
    assert not is_sensitive(Path("environment.py"))

def test_is_sensitive_keys():
    assert is_sensitive(Path("private.pem"))
    assert is_sensitive(Path("cert.p12"))
    assert is_sensitive(Path("id_rsa"))
    assert is_sensitive(Path("aws_credentials.ini"))
    assert not is_sensitive(Path("rsa_utils.py"))

def test_is_sensitive_passwords():
    assert is_sensitive(Path(".htpasswd"))
    assert is_sensitive(Path("db_password.txt"))
    assert not is_sensitive(Path("password_validator.py"))

def test_safe_files():
    assert not is_sensitive(Path("main.py"))
    assert not is_sensitive(Path("src/utils/helper.js"))
    assert not is_sensitive(Path("tests/test_model.py"))
    assert not is_sensitive(Path("package.json"))
