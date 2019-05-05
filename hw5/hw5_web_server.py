from flask import Flask, jsonify, request, render_template
import uuid
import subprocess
import os
import boto3
import datetime
import botocore
import requests
import time

app = Flask(__name__)

@app.route('/', methods=['GET'])
# This method is called when a user visits "/" on your server
def home():
    # substitute your favorite geek message below
    return "ZORK I: The Great Underground Empire."


@app.route('/hello', methods=['GET'])
# This method is called when a user visits "/hello" on your server
def hello():
    # another geek message here!
    return "West of House<br ><br />&gt; _"


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'code': 'HTTP_400_BAD_REQUEST',
        'status': 'error',
        'message': 'Key not found, please try again.'
    })

@app.errorhandler(404)
def bad_request(error):
    return jsonify({
        'code': 'HTTP_404_NOT_FOUND',
        'status': 'error',
        'message': 'URL not found, please try again.'
    })

@app.route('/annotate', methods=['GET'])
def annotate():
    # Define S3 policy fields and conditions
    # used https://stackoverflow.com/questions/36287720/boto3-get-credentials-dynamically
    # used https://boto3.amazonaws.com/v1/documentation/api/latest/reference/core/boto3.html

    # generate uuid
    ID = uuid.uuid4()

    # create client
    s3 = boto3.client('s3', region_name='us-east-1', config=botocore.client.Config(signature_version='s3v4'))

    # define parameters
    bucket = 'gas-inputs'
    user = 'UserX'
    key = 'atinn/{}/'.format(user)+str(ID)+'/${filename}'
    url = '{}/job'.format(request.url)

    if '${filename}' == '':
        file_does_not_exist()

    conditions = [{"acl": "private"},
                  ["starts-with", "$success_action_redirect", url],
                  ["starts-with", "$key", "atinn/"]]
    expires = 300  # 5 minutes

    #input parameters
    s3 = s3.generate_presigned_post(Bucket=bucket,
                                    Key=key,
                                    Conditions=conditions,
                                    ExpiresIn=expires)

    # retrieve relevant data
    policy = s3['fields']['policy']
    signature = s3['fields']['x-amz-signature']
    AWSaccesskeyid = s3['fields']['x-amz-credential']
    security_token = s3['fields']['x-amz-security-token']
    algorithm = s3['fields']['x-amz-algorithm']
    date = s3['fields']['x-amz-date']

    return render_template("annotate.html", bucket_name=bucket, key=key, acl='private', policy=policy,
                           signature=signature, aws_key=AWSaccesskeyid, security_token=security_token,
                           X_Amz_Algorithm=algorithm, date=date, url=url)

@app.route("/annotate/job", methods=["GET"])
def annotate_job():

    # Get bucket name, key, and job ID from the S3 redirect URL
    bucket = request.args.get('bucket')
    key = request.args.get('key') # 'atinn/UserX/UUID/filename'
    job_ID = key.partition('/')[2].partition('/')[2].partition('/')[0]
    filename = key.partition('/')[2].partition('/')[2].partition('/')[2]

    # Create a job item and persist it to the annotations database
    try:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        ann_table = dynamodb.Table('atinn_annotations')
        data = {  "job_id": str(job_ID),
                  "user_id": 'userX',
                  "input_file_name": str(filename),
                  "s3_inputs_bucket": str(bucket),
                  "s3_key_input_file": str(key),
                  "submit_time": int(time.time()),
                  "job_status": "PENDING"
                }

        # upload to the database
        ann_table.put_item(Item=data)

        # POST job request to the annotator
        ann_job_response = requests.post('http://atinn-hw5-ann.ucmpcs.org:5000/annotations', data=data)
        return (ann_job_response.text)
    except botocore.exceptions.ClientError:
        return jsonify({
                        'code': 'HTTP_500_INTERNAL_SERVER_ERROR',
                        'status': 'error',
                        'message': 'Error entering in the database'
                        })

# Run the app server
app.run(host='0.0.0.0', debug=True)