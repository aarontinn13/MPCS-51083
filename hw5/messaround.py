import boto3

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
ann_table = dynamodb.Table('atinn_annotations')
response = ann_table.get_item(Key={'job_id': '5d2dff58-847b-4bdf-93f9-559846b39d85'})
status = response['Item']['job_status']
print(status)