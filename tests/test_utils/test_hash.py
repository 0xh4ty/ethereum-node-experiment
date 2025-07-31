#!/usr/bin/env python3

import timeit

from ethereum_node.utils.hash import keccak256


def test_keccak256_known():
    assert keccak256(b"") == bytes.fromhex(
        "c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470"
    )
    assert keccak256(b"hello") == bytes.fromhex(
        "1c8aff950685c2ed4bc3174f3472287b56d9517b9c948127319a09a7a36deac8"
    )


'''Uncomment the below test to check keccak256 performance
def test_keccak256_performance():
    # Time 1 million calls to keccak256(b"hello")
    total_time = timeit.timeit(lambda: keccak256(b"hello"), number=1_000_000)
    avg_time_ns = (total_time / 1_000_000) * 1e9  # Convert to nanoseconds
    print(f"Avg keccak256 time: {avg_time_ns:.2f} ns")

    # Assert performance goal
    assert avg_time_ns < 4000, f"Too slow: {avg_time_ns:.2f} ns per call"
'''
