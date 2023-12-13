import bcrypt


def hash_password(plaintext: str):
    plaintext_bytes = plaintext.encode("utf-8")
    hashed_bytes = bcrypt.hashpw(plaintext_bytes, bcrypt.gensalt())
    hashed = hashed_bytes.decode("utf-8")
    return hashed


def are_passwords_equal(input_plaintext: str, stored_hash: str):
    input_plaintext_bytes = input_plaintext.encode("utf-8")
    stored_hash_bytes = stored_hash.encode("utf-8")
    return bcrypt.checkpw(input_plaintext_bytes, stored_hash_bytes)
