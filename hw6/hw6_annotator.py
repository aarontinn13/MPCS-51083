import subprocess
import os
import boto3
import botocore
import json

def annotations():

    # Connect to SQS and get the message queue https: // boto3.amazonaws.com / v1 / documentation / api / latest / guide / sqs.html
    # Used this resource as well: https://boto3.amazonaws.com/v1/documentation/api/latest/guide/sqs-example-sending-receiving-msgs.html
    # Used this resource as well: https://boto3.amazonaws.com/v1/documentation/api/latest/guide/sqs-example-long-polling.html
    sqs = boto3.client('sqs', region_name='us-east-1')
    queue_url = 'https://sqs.us-east-1.amazonaws.com/127134666975/atinn_job_requests'
    sqs.set_queue_attributes(QueueUrl=queue_url,Attributes={'ReceiveMessageWaitTimeSeconds': '20'})

    # Poll the message queue in a loop
    while True:
        try:
            # Attempt to read a message from the queue
            queue = sqs.receive_message(QueueUrl=queue_url)
            receipt_handle = queue['Messages'][0]['ReceiptHandle']
            message = json.loads(queue['Messages'][0]['Body'])
            message = json.loads(message['Message'])
        except KeyError:
            # no messages in the queue, keep listening...
            continue

        # If message read, extract job parameters from the message body as before
        key = message['s3_key_input_file']
        path = '/'.join(key.split('/')[0:3])
        ID = message['job_id']
        filename = message['input_file_name']
        bucket = message['s3_inputs_bucket']

        # create new UUID folder in ./jobs https://stackoverflow.com/questions/18973418/os-mkdirpath-returns-oserror-when-directory-does-not-exist
        try:
            create_ID_folder = 'mkdir ./jobs/{}'.format(ID)
            os.system(create_ID_folder)
        except OSError:
            print('could not make directory.')

        # download the file https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-example-download-file.html
        s3_client = boto3.resource('s3', region_name='us-east-1')
        s3_client.meta.client.download_file(bucket, key, '{}'.format(filename))

        # move the file to temporary directory
        if os.path.exists('./{}'.format(filename)):
            move_file = 'mv ./{} ./jobs/{}'.format(filename, ID)
            os.system(move_file)
        else:
            print('file does not exist')

        # start the dynamoDB table
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        ann_table = dynamodb.Table('atinn_annotations')

        # check the status on the job https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/GettingStarted.Python.03.html
        response = ann_table.get_item(Key={'job_id': ID})
        status = response['Item']['job_status']

        # handle if the job is already complete
        if status == 'COMPLETED':
            print({"code": 200,
                    "data": {
                        "job_id": ID,
                        "input_file": filename,
                            },
                    "Comment": "Job is already complete!"
                    })
        try:
            # update the dynamoDB table status to running https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/GettingStarted.Python.03.html
            ann_table.update_item( Key= {'job_id': ID},
                                   UpdateExpression="set job_status = :s",
                                   ExpressionAttributeValues={':s': 'RUNNING'},
                                   ReturnValues="UPDATED_NEW"
                                 )
        # cannot find key
        except botocore.exceptions.ClientError:
            print({
                    'code': 'HTTP_500_INTERNAL_SERVER_ERROR',
                    'status': 'error',
                    'message': 'Cannot find that key'
                    })

        # spawn a subprocess
        try:
            subprocess.Popen(['sh', '-c', 'cd ./anntools && python hw6_run.py ../jobs/{ID}/{filename} {ID} {filename} {path}'.format(ID=ID, filename=filename, path=path)])

        except subprocess.CalledProcessError:
            print({
                'code': 'HTTP_500_INTERNAL_SERVER_ERROR',
                'status': 'error',
                'message': 'Server could not process request, please try again later.'
            })

        # Delete the message from the queue, if job was successfully submitted
        # https://boto3.amazonaws.com/v1/documentation/api/latest/guide/sqs-example-sending-receiving-msgs.html
        sqs.delete_message(QueueUrl=queue_url,ReceiptHandle=receipt_handle)

        print({"code": 201,
                        "data": {
                            "job_id": ID,
                            "input_file": filename,
                        }
                        })

annotations()

