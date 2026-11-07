import pyotp

ISSUER = 'microblog'


def generate_secret():
    return pyotp.random_base32()


def provisioning_uri(secret, email):
    return pyotp.TOTP(secret).provisioning_uri(name=email, issuer_name=ISSUER)


def verify_code(secret, code):
    return bool(secret) and pyotp.TOTP(secret).verify(code, valid_window=1)
