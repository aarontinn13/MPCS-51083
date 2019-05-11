from flask import Flask, jsonify, request
import uuid
import subprocess
import os
import boto3

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


# any additional errors that were not caught
@app.errorhandler(Exception)
def all_exception_handler(error):
    return jsonify({
        'code': 'HTTP_500_INTERNAL_SERVER_ERROR',
        'status': 'error',
        'message': 'An error has occured please try again.'
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

@app.route('/annotations', methods=['GET'])
def annotations():

    # forget what stack overflow post I took this from, but I took it from that site :/
    bucket = request.args.get('bucket')
    key = request.args.get('key')


    # get the UUID and file name
    name = key.split('/')
    path = '/'.join(name[0:2])
    ID = name[2]
    filename = name[3]

    # create new UUID folder in ./jobs
    create_ID_folder = 'mkdir ./jobs/{}'.format(ID)
    os.system(create_ID_folder)

    # download the file https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-example-download-file.html
    s3_client = boto3.resource('s3', region_name='us-east-1')
    s3_client.meta.client.download_file(bucket, key, '{}'.format(filename))

    # move the file to temporary directory
    move_file = 'mv ./{} ./jobs/{}'.format(filename, ID)
    os.system(move_file)

    # spawn a subprocess
    try:
        subprocess.Popen(['sh', '-c', 'cd ./anntools && python hw6_run.py ../jobs/{ID}/{filename} {ID} {filename} {path}'.format(ID=ID, filename=filename, path=path)])
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
