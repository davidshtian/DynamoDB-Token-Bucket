import boto3
from botocore.exceptions import ClientError
import time
import uuid


class DynamoDBTokenBucket:
    def __init__(self, table_name, max_tokens=10, token_timeout_seconds=300):
        self.dynamodb = boto3.resource('dynamodb')
        self.table_name = table_name
        self.table = self.dynamodb.Table(table_name)
        self.max_tokens = max_tokens
        self.token_timeout = token_timeout_seconds

    def initialize_bucket(self):
        """Initialize the token bucket with max tokens"""
        try:
            self.table.put_item(
                Item={
                    'bucket_id': 'token_bucket',
                    'available_tokens': self.max_tokens,
                    'in_use_tokens': {}
                },
                ConditionExpression='attribute_not_exists(bucket_id)'
            )
        except ClientError as e:
            if e.response['Error']['Code'] != 'ConditionalCheckFailedException':
                raise

    def cleanup_expired_tokens(self):
        """Cleanup expired tokens and return them to the pool"""
        try:
            response = self.table.get_item(
                Key={'bucket_id': 'token_bucket'},
                ProjectionExpression='in_use_tokens'
            )

            if 'Item' not in response:
                return

            in_use_tokens = response['Item'].get('in_use_tokens', {})
            current_time = int(time.time())
            expired_tokens = []

            # Find expired tokens
            for token_id, timestamp in in_use_tokens.items():
                if current_time - timestamp > self.token_timeout:
                    expired_tokens.append(token_id)

            # Release each expired token
            for token_id in expired_tokens:
                try:
                    self.table.update_item(
                        Key={'bucket_id': 'token_bucket'},
                        UpdateExpression='REMOVE in_use_tokens.#token ADD available_tokens :increment',
                        ConditionExpression='attribute_exists(in_use_tokens.#token)',
                        ExpressionAttributeNames={
                            '#token': token_id
                        },
                        ExpressionAttributeValues={
                            ':increment': 1
                        }
                    )
                    print(f"Cleaned up expired token: {token_id}")
                except ClientError:
                    continue

        except ClientError:
            pass

    def acquire_token(self, timeout_seconds=30):
        """
        Try to acquire a token from the bucket
        Returns: (token_id, success)
        """
        # Cleanup expired tokens before attempting to acquire
        self.cleanup_expired_tokens()

        token_id = str(uuid.uuid4())
        start_time = time.time()

        while time.time() - start_time < timeout_seconds:
            try:
                response = self.table.update_item(
                    Key={'bucket_id': 'token_bucket'},
                    UpdateExpression='SET in_use_tokens.#token = :timestamp ADD available_tokens :decrement',
                    ConditionExpression='available_tokens > :zero AND (attribute_not_exists(in_use_tokens.#token) OR in_use_tokens.#token = :none)',
                    ExpressionAttributeNames={
                        '#token': token_id
                    },
                    ExpressionAttributeValues={
                        ':timestamp': int(time.time()),
                        ':zero': 0,
                        ':decrement': -1,
                        ':none': None
                    },
                    ReturnValues='UPDATED_NEW'
                )
                return token_id, True
            except ClientError as e:
                if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                    time.sleep(0.1)  # Wait before retrying
                    continue
                raise

        return None, False

    def reset_bucket(self):
        """Reset the bucket to initial state with max tokens"""
        try:
            self.table.update_item(
                Key={'bucket_id': 'token_bucket'},
                UpdateExpression='SET available_tokens = :max, in_use_tokens = :empty',
                ExpressionAttributeValues={
                    ':max': self.max_tokens,
                    ':empty': {}
                }
            )
            return True
        except ClientError:
            return False

    def release_token(self, token_id):
        """Release a token back to the bucket"""
        try:
            response = self.table.update_item(
                Key={'bucket_id': 'token_bucket'},
                UpdateExpression='REMOVE in_use_tokens.#token ADD available_tokens :increment',
                ConditionExpression='attribute_exists(in_use_tokens.#token)',
                ExpressionAttributeNames={
                    '#token': token_id
                },
                ExpressionAttributeValues={
                    ':increment': 1
                },
                ReturnValues='UPDATED_NEW'
            )
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                print(
                    f"Warning: Token {token_id} was already released or doesn't exist")
            return False
