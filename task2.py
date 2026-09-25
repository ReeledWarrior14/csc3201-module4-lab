import multiprocessing
import time
import bcrypt
from nltk.corpus import words


def check_list(candidates, hashed, stop_flag):
    """Check a chunk of candidate words against a single hash.

    `hashed` is the full bcrypt hash string (e.g. "$2b$08$J9FW66..."),
    which already contains the salt and cost factor embedded inside it.

    `stop_flag` is a multiprocessing.Value shared across workers; once one
    worker finds the password it sets the flag so the others can bail out
    early instead of wasting time on an already-solved hash.
    """
    hashed_bytes = hashed.encode('utf-8')

    for word in candidates:
        # another worker already found the password -- stop hashing
        if stop_flag.value:
            return None

        # bcrypt truncates at 72 bytes (and is case-sensitive);
        # encode as-is.
        if bcrypt.checkpw(word.encode('utf-8'), hashed_bytes):
            stop_flag.value = True
            return word

    return None


def chunked(lst, n):
    """Split a list into n roughly-equal contiguous chunks (last takes remainder)."""
    size = len(lst) // n
    remainder = len(lst) % n
    chunks = []
    i = 0
    for k in range(n):
        extra = 1 if k < remainder else 0
        chunks.append(lst[i:i + size + extra])
        i += size + extra
    return chunks


def main():
    # Load the list of words from NLTK
    word_list = words.words()

    # filter to 6-10 letter words
    filtered_words = [word for word in word_list if 6 <= len(word) <= 10]

    # get passwords from file
    with open('passwords.txt', 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    # Parse each line into (username, full_bcrypt_hash)
    accounts = []
    for line in lines:
        username, hashed = line.split(':', 1)
        accounts.append((username, hashed))

    workers = multiprocessing.cpu_count()
    chunks = chunked(filtered_words, workers)

    results_summary = []
    start_total = time.time()

    # One pool reused for all passwords (avoids re-spawning workers each time)
    with multiprocessing.Manager() as manager, multiprocessing.Pool(processes=workers) as pool:

        for username, hashed in accounts:
            # fresh shared flag per password
            stop_flag = manager.Value('b', False)

            t0 = time.time()
            results = pool.starmap(
                check_list,
                [(chunk, hashed, stop_flag) for chunk in chunks],
            )
            found = next((r for r in results if r is not None), None)
            elapsed = time.time() - t0

            if found:
                results_summary.append((username, found))
                print(f"{username}: {found}  (took {elapsed:.2f}s)")
            else:
                print(f"{username}: NOT FOUND  (took {elapsed:.2f}s)")

    total = time.time() - start_total
    print(f"\nCracked {len(results_summary)} of {len(accounts)} passwords.")
    print(f"Total time: {total:.2f}s")


if __name__ == '__main__':
    main()

