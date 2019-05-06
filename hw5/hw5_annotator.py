from flask import Flask, jsonify, request
import uuid
import subprocess
import os
import boto3
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
        'message': 'This file does not exist, please choose a file [free_1.vcf, free_2.vcf, premium_1.vcf, premium_2.vcf, premium_3.vcf, test.vcf]'
    })


def UUID_does_not_exist():
    return jsonify({
        'code': 'HTTP_500_INTERNAL_SERVER_ERROR',
        'status': 'error',
        'message': 'This UUID does not exist'
    })

@app.route('/annotations', methods=['POST'])
def annotations():

    # forget what stack overflow post I took this from, but I took it from that site :/
    # get the UUID and file name
    key = request.form['s3_key_input_file']
    path = '/'.join(key.split('/')[0:3])
    ID = request.form['job_id']
    filename = request.form['input_file_name']
    bucket = request.form['s3_inputs_bucket']

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
        return jsonify({"code": 200,
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
    # cannot
    except botocore.exceptions.ClientError:
        return jsonify({
                        'code': 'HTTP_500_INTERNAL_SERVER_ERROR',
                        'status': 'error',
                        'message': 'Cannot find that key'
                        })

    # spawn a subprocess
    try:
        subprocess.Popen(['sh', '-c', 'cd ./anntools && python hw5_run.py ../jobs/{ID}/{filename} {ID} {filename} {path}'.format(ID=ID, filename=filename, path=path)])

    except subprocess.CalledProcessError:
        return jsonify({
            'code': 'HTTP_500_INTERNAL_SERVER_ERROR',
            'status': 'error',
            'message': 'Server could not process request, please try again later.'
        })

    return jsonify({"code": 201,
                    "data": {
                        "job_id": ID,
                        "input_file": filename,
                    }
                    })

# Run the app server
app.run(host='0.0.0.0', debug=True)
