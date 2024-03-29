import boto3

topic_arn = "arn:aws:sns:"

def send_sns(message, subject):
    try:
        client = boto3.client("sns")
        result = client.publish(TopicArn=topic_arn, Message=message, Subject=subject)
        if result['ResponseMetadata']['HTTPStatusCode'] == 200:
            print("Notification sent successfully!")
            return True
    except Exception as e:
        print("Error occurred while publishing notification: ", e)
        return False

def lambda_handler(event, context):
    # Create an S3 client
    s3 = boto3.client('s3')

    # List all buckets in your account
    response = s3.list_buckets()

    public_buckets = []
    private_buckets = []

    print(event)

    for bucket in response['Buckets']:
        try:
            response = s3.get_public_access_block(Bucket=bucket['Name'])
            if response['PublicAccessBlockConfiguration']['BlockPublicAcls'] or response['PublicAccessBlockConfiguration']['IgnorePublicAcls'] or response['PublicAccessBlockConfiguration']['BlockPublicPolicy'] or response['PublicAccessBlockConfiguration']['RestrictPublicBuckets']:
                print(f"{bucket['Name']} does not have public access.")
                private_buckets.append(bucket['Name'])
            else:
                print(f"{bucket['Name']} has public access.")
                public_buckets.append(bucket['Name'])
        except Exception as e:
            print(f"Error checking Block Public Access settings for {bucket['Name']}: {e}")
    
    # Construct message
    message = f"Public buckets: {public_buckets}\nPrivate buckets: {private_buckets}"
    subject = "Bucket Public Access Check"
    
    # Send SNS notification
    SNSResult = send_sns(message, subject)
    if SNSResult:
        print("Notification Sent..") 
    else:
        return False
    
    return {
        'statusCode': 200,
        'body': 'Check complete.'
    }