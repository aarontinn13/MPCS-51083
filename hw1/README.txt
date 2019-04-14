--------------------------------------------------------------------------------------------------------------------------------
Specs:

    Ubuntu 18.04
    Python 3.5

--------------------------------------------------------------------------------------------------------------------------------
Running the Python Script:

    python hw1.py

--------------------------------------------------------------------------------------------------------------------------------
Output (Should be similar):

    Instance ID: i-05d90df919c1a9f30
    Launched at 2019-04-05 22:56:44+00:00 in availability zone us-east-1d
    This instance has termination protection set...
    Instance termination Failed
    The instance i-05d90df919c1a9f30 may not be terminated. Modify its 'disableApiTermination' instance attribute and try again.

    Instance ID: i-0aab6964a2a9d02d8
    Launched at 2019-04-05 22:59:56+00:00 in availability zone us-east-1d
    This instance does not have termination protection set...Attempting to set protection...
    This instance has already been terminated
    Instance has been Terminated!

    Number of EBS Volumes: 34
    Total provisioned storage (GB):  272

    Port      Inbound IP Address Ranges(s)
    ----    -------------------------------
    5432    ['0.0.0.0/0']
    4433    ['0.0.0.0/0']
    5000    ['0.0.0.0/0', '34.229.171.92/30']
    8089    ['0.0.0.0/0']
    3306    ['0.0.0.0/0']
    445     ['98.253.27.0/24']
    443     ['0.0.0.0/0']

--------------------------------------------------------------------------------------------------------------------------------
Reading the ssh_session.txt (or view clean_session.txt directly):

    cat ssh_session.txt

--------------------------------------------------------------------------------------------------------------------------------
Comments:

    - Everything seems to be working okay.

    - The relevant files in the repository are:

        hw1.py
        ssh_session.txt
        clean_session.txt (optional)
        README.txt

    - This script also assumes I am logged into the aws and I do not need to provide any further credentials

    - Reading the ssh_session.txt file in a text editor has alot of strange symbols when generating the txt file using:

        script ssh_session.txt

     thus it is best to view the document via the terminal by using cat command, or view the clean_session.txt directly
     which has the symbols removed.

    - There should be 4 commands seen in the ssh_session.txt / clean_session.txt. Just in case I will paste them below:

        aws ec2 run-instances --image-id ami-0ce8936181a9b7073 --count 1 --instance-type t2.nano --key-name atinn
        --security-groups mpcs

        aws ec2 create-tags --resources i-0d760b042907ebfbc --tags Key=Name,Value=atinn

        aws ec2 run-instances --image-id ami-0ce8936181a9b7073 --count 1 --instance-type t2.nano --key-name atinn
        --security-groups mpcs --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=atinn}]'

        ssh -i ~/.ssh/atinn.pem ubuntu@ec2-204-236-198-84.compute-1.amazonaws.com