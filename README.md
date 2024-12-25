# DynamoDB Token Bucket

A distributed token bucket implementation using Amazon DynamoDB for rate limiting and concurrency control.

## Overview

This package provides a distributed token bucket implementation that uses Amazon DynamoDB as the backend storage. It's useful for:
- Rate limiting across distributed systems
- Controlling concurrent access to resources
- Managing distributed semaphores

## Features

- Distributed token management
- Automatic cleanup of expired tokens
- Configurable token limits and timeouts
- Thread-safe operations
- Handles failure scenarios gracefully

## Prerequisites

- Python 3.6+
- boto3
- AWS credentials configured
- DynamoDB access permissions

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd ddb-token
```

2. Install dependencies:
```bash
pip install boto3
```

3. Create the DynamoDB table:
```bash
python create_table.py
```

## Usage

### Basic Example

```python
from token_bucket import DynamoDBTokenBucket

# Initialize the bucket
bucket = DynamoDBTokenBucket('token_bucket', max_tokens=10, token_timeout_seconds=300)
bucket.initialize_bucket()

# Acquire a token
token_id, success = bucket.acquire_token(timeout_seconds=30)
if success:
    try:
        # Do your work here
        print(f"Got token: {token_id}")
    finally:
        # Release the token
        bucket.release_token(token_id)
```

### Advanced Usage

See `example.py` for a more complex example demonstrating:
- Multiple concurrent workers
- Handling token acquisition timeouts
- Simulated failure scenarios
- Automatic token cleanup

## API Reference

### DynamoDBTokenBucket

#### Constructor
```python
DynamoDBTokenBucket(table_name, max_tokens=10, token_timeout_seconds=300)
```

#### Methods

- `initialize_bucket()`: Initialize the token bucket with maximum tokens
- `acquire_token(timeout_seconds=30)`: Attempt to acquire a token
- `release_token(token_id)`: Release a token back to the bucket
- `cleanup_expired_tokens()`: Clean up expired tokens
- `reset_bucket()`: Reset the bucket to its initial state

## Implementation Details

The implementation uses DynamoDB's atomic operations to ensure thread-safety and consistency:
- Tokens are tracked using a single DynamoDB item
- Conditional updates prevent race conditions
- Expired tokens are automatically cleaned up
- Failed operations are handled gracefully

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

You may want to customize:
- The repository URL in the installation section
- The license type
- Any specific contribution guidelines
- Additional examples or use cases specific to your needs
