from flask import Flask, jsonify, request
import uuid
import subprocess
import os

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


def file_does_not_exist():
    return "This file does not exist"


def UUID_does_not_exist():
    return "This UUID does not exist"


@app.route('/annotations', methods=['POST', 'GET'])
@app.route('/annotations/<id>', methods=['POST', 'GET'])
def annotations(id=None):
    # handle GET
    if request.method == 'GET':

        # Retrieve annotation job status and log
        if id:

            # Check if UUID exists
            exists = os.path.isdir('./jobs/{}'.format(id))
            if not exists:
                return UUID_does_not_exist()

            # If job exists and job is complete
            if any(fname.endswith('.annot.vcf') for fname in os.listdir('./jobs/{}'.format(id))):
                log_file = [f for f in os.listdir('./jobs/{}'.format(id)) if f.endswith('.log')][0]
                with open('./jobs/{}/{}'.format(id, log_file), 'r') as log:
                    return jsonify({
                        "code": 200,
                        "data": {
                            "job_id": "{}".format(id),
                            "job_status": "completed",
                            "log": log.read()
                        }
                    })

            # If job exists, but job is incomplete
            else:
                return jsonify({
                    "code": 200,
                    "data": {
                        "job_id": "{}".format(id),
                        "job_status": "running"
                    }
                })

        # Retrieve list of annotation jobs
        else:

            jobs = []

            for job_id in os.listdir('./jobs'):
                if any(fname.endswith('.annot.vcf') for fname in os.listdir('./jobs/{}'.format(job_id))):
                    log_file = [f for f in os.listdir('./jobs/{}'.format(job_id)) if f.endswith('.log')][0]
                    with open('./jobs/{}/{}'.format(job_id, log_file), 'r') as log:
                        jobs.append({
                            "job_id": job_id,
                            "job_details": {
                                "job_status": "completed",
                                "log": log.read()
                            }
                        })

                # If job exists, but job is incomplete
                else:
                    jobs.append({
                        "job_id": job_id,
                        "job_details": {
                            "job_id": "{}".format(job_id),
                            "job_status": "running"
                        }
                    })

            return jsonify({
                "code": 200,
                "data": {
                    "jobs": jobs
                }
            })

    # submit an annotation job
    elif request.method == 'POST':

        # get the input
        if request.is_json:
            data = request.get_json()
            input_file = data['input_file']
        if not request.is_json:
            input_file = request.form['input_file']

        # check whether the input is valid or not
        exists = os.path.isfile('./anntools/data/{}'.format(input_file))
        if not exists:
            return file_does_not_exist()

        # generate a UUID
        UUID = uuid.uuid1()

        # create new UUID folder in ./jobs
        create_UUID_folder = 'mkdir ./jobs/{}'.format(UUID)
        os.system(create_UUID_folder)

        # copy input_file from data into the UUID folder
        copy_file = 'cp ./anntools/data/{} ./jobs/{}'.format(input_file, UUID)
        os.system(copy_file)

        # spawn a subprocess
        subprocess.Popen(['sh', '-c', 'cd ./anntools && python run.py ../jobs/{}/{}'.format(UUID, input_file)])

        return jsonify({"code": 201,
                        "data": {
                            "job_id": UUID,
                            "input_file": input_file,
                        }
                        })


# Run the app server
app.run(host='0.0.0.0', debug=True)
