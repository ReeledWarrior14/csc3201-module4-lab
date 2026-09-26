from __future__ import annotations
import hashlib
import random
import string
import time


def sha256_hash(input_str: str) -> str:
    string = bytes(input_str.encode('utf-8'))
    return hashlib.sha256(string).hexdigest()

def truncate_hash(hash: str, bits: int) -> int:
    #convert hash to integer 
    hash_to_int = int(hash, 16)
    #start with 256-bit hash and shift everything except the starting bits
    return hash_to_int >> (256-bits)

def hamming_distance(s1, s2):
    if len(s1) != len(s2):
        raise ValueError("Strings must be of the same length")
    count = 0
    for c1, c2 in zip(s1, s2):
        if c1 != c2:
            count += (c1 ^ c2).bit_count()
    return count

def find_hamming_distance_1():
    base = random.choices(string.ascii_lowercase + string.digits, k=10)
    base = bytearray("".join(base).encode('utf-8'))

    for i in base:
        # flip ith bit
        # base[i % len(base)] ^= 1 << (i % 8)
        modified = base[:]
        modified[i % len(base)] ^= 1 << (i % 8)

        if hamming_distance(base, modified) == 1:

            # make sure we can utf8 decode
            try:
                base.decode('utf-8')
                modified.decode('utf-8')
            except UnicodeDecodeError:
                continue

            return base, modified

    return None, None

def find_collision(bits, max_attempts=1000000000):
    seen = {}
    now = time.perf_counter_ns()

    for attempts in range(max_attempts):
        s = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        h = truncate_hash(sha256_hash(s), bits)

        if h in seen:
            end_time = time.perf_counter_ns() - now
            return seen[h], s, attempts + 1, end_time / 1e9
        else:
            seen[h] = s

    end_time = time.perf_counter_ns() - now
    return None, None, max_attempts, end_time / 1e9

def task_1a():
    print("Task 1a: SHA256 hashes of arbitrary inputs")
    for input in ["Hello, World!", "Python", "Cryptography"]:
        hash_value = sha256_hash(input)
        print(f"\nInput: {input} -> SHA256 Hash: {hash_value}")

def task_1b():
    print("\n\nTask 1b: Strings with Hamming distance of 1")
    for i in range(1, 4):
        s1, s2 = find_hamming_distance_1()
        while s1 is None or s2 is None:
            s1, s2 = find_hamming_distance_1()

        # calc hashes
        h1 = sha256_hash(s1.decode('utf-8'))
        h2 = sha256_hash(s2.decode('utf-8'))
        print(f"\nBase: {s1}, Modified: {s2}")
        print(f"Base Hash: {h1}, Modified Hash: {h2}")

def task_1c():
    print("\n\nTask 1c: Finding collisions for truncated hashes")
    bits = []
    times = []
    inputs = []
    num_of_inputs = []

    for size in range(8, 51, 2):
        s1, s2, attempts, elapsed_time = find_collision(size)
        if s1 is not None and s2 is not None:
            print(f"Collision found for {size} bits: {s1} and {s2} in {attempts} attempts, time taken: {elapsed_time:.6f} seconds")
            bits.append(size)
            times.append(elapsed_time)
            inputs.append((s1, s2))
            num_of_inputs.append(attempts)
        else:
            print(f"No collision found for {size} bits after {attempts} attempts, time taken: {elapsed_time:.6f} seconds")

    print(f"\nBits: {bits}")
    print(f"Times: {times}")
    print(f"Number of inputs: {num_of_inputs}")


def task_1_main():
    task_1a()
    task_1b()
    task_1c()

task_1_main()
