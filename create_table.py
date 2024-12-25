import boto3


def create_token_bucket_table(table_name):
    dynamodb = boto3.resource('dynamodb')

    table = dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {
                'AttributeName': 'bucket_id',
                'KeyType': 'HASH'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'bucket_id',
                'AttributeType': 'S'
            }
        ],
        BillingMode='PAY_PER_REQUEST'
    )

    table.wait_until_exists()
    return table


if __name__ == '__main__':
    table = create_token_bucket_table('token_bucket')
    print(f"Table {table.table_name} created successfully")
