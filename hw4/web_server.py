from flask import Flask, jsonify, request, render_template
import uuid
import subprocess
import os
import boto3
import datetime
import botocore

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

def file_does_not_exist():
    return jsonify({
        'code': 'HTTP_500_INTERNAL_SERVER_ERROR',
        'status': 'error',
        'message': 'please choose a file'
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
    if '${filename}' == '':
        file_does_not_exist()

    conditions = [{"acl": "private"},
                  ["starts-with", "$success_action_redirect","http://atinn-hw4-ann.ucmpcs.org:5000/annotations"],
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
                           signature=signature, aws_key=AWSaccesskeyid, security_token=security_token, X_Amz_Algorithm=algorithm,
                           date=date)

@app.route('/annotate/files', methods=['GET'])
def files():
    # used https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html for list objects function

    files = []
    s3 = boto3.client("s3", region_name='us-east-1')
    all_objects = s3.list_objects(Bucket='gas-inputs', Prefix='atinn')
    for i in all_objects['Contents']:
        if i['Key'].partition('/')[2] != '':
            files.append(i['Key'])
    return jsonify({
              "code": 200,
              "data": {
                "files":files
                      }
                   })

# Run the app server
app.run(host='0.0.0.0', debug=True)
