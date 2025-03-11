import secrets  # Cryptographically secure random number generator

# Large prime number (P) and generator (G)
# Using a 2048-bit safe prime from RFC 3526 Group 14
P = int(
    "FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74"
    "020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF25F1437"
    "4FE1356D6D51C245E485B576625E7EC6F44C42E9A63A36210000000000090563",
    16,
)
G = 2  # Generator for Group 14

# Generate a secure private key
def generate_private_key():
    """
    Generates a private key securely using the secrets module.
    The private key is a random number between 1 and P-1.
    """
    return secrets.randbelow(P - 1) + 1

# Compute public key (G^private_key % P)
def compute_public_key(private_key, P, G):
    """
    Computes the public key for Diffie-Hellman.
    """
    return pow(G, private_key, P)

# Compute shared secret (peer_public_key^private_key % P)
def compute_shared_secret(private_key, peer_public_key, P):
    """
    Computes the shared secret using the peer's public key and own private key.
    """
    return pow(peer_public_key, private_key, P)
