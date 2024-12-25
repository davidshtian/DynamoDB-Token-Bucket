from token_bucket import DynamoDBTokenBucket
import threading
import time
import random


def worker(bucket, worker_id, simulate_failure=False):
    token_id, success = bucket.acquire_token(timeout_seconds=5)
    if success:
        print(f"Worker {worker_id} acquired token {token_id}")
        # Simulate some work
        time.sleep(random.randint(1, 9))

        if simulate_failure and random.random() < 0.3:  # 30% chance of failure
            print(f"Worker {worker_id} failed to release token {token_id}")
            return

        bucket.release_token(token_id)
        print(f"Worker {worker_id} released token {token_id}")
    else:
        print(f"Worker {worker_id} failed to acquire token")


def main():
    bucket = DynamoDBTokenBucket('token_bucket', token_timeout_seconds=30)
    bucket.initialize_bucket()

    # First round with some simulated failures
    print("First round with simulated failures:")
    threads = []
    for i in range(15):
        thread = threading.Thread(target=worker, args=(bucket, i, True))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    time.sleep(35)  # Wait for token timeout

    # Second round after cleanup
    print("\nSecond round after cleanup:")
    threads = []
    for i in range(15, 30):
        thread = threading.Thread(target=worker, args=(bucket, i, False))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()


if __name__ == '__main__':
    main()
