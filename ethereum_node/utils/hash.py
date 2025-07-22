from eth_hash.auto import keccak


def keccak256(data: bytes) -> bytes:
    return keccak(data)
