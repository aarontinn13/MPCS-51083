'''
A lot of the code snippets I extracted from were in the documentation
https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html
'''

import boto3
import botocore
from tabulate import tabulate

def instance_protect(name):

    # get the client
    ec2client = boto3.client('ec2')

    # find all instances
    response = ec2client.describe_instances()

    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:

            #if we have found our instance by cnetID
            if instance['KeyName'] == name:
                print('Instance ID: {}'.format(instance['InstanceId']))
                print('Launched at {} in availability zone {}'.format(instance['LaunchTime'],
                                                                      instance['Placement']['AvailabilityZone']))

                # check termination protection
                attribute = ec2client.describe_instance_attribute(Attribute='disableApiTermination', InstanceId=instance['InstanceId'])

                # if False, set termination protection
                if attribute['DisableApiTermination']['Value'] == False:
                    print('This instance does not have termination protection set...Attempting to set protection...')
                    ec2client.modify_instance_attribute(DisableApiTermination={'Value':True}, InstanceId=instance['InstanceId'])
                    print('This instance now has termination protection set...')
                else:
                    print('This instance has termination protection set...')

                # attempt to terminate
                try:
                    ec2client.terminate_instances(InstanceIds=[instance['InstanceId']])
                    print('Instance has been Terminated!')
                except botocore.exceptions.ClientError:
                    print('Instance termination Failed')
                    print('The instance {} may not be terminated. Modify its \'disableApiTermination\' instance attribute and try again.'.format(instance['InstanceId']))
                print()

def ebs_profile():
    ec2client = boto3.resource('ec2')
    volumes = [volume.size for volume in ec2client.volumes.all()]
    print('Number of EBS Volumes:', len(volumes))
    print('Total provisioned storage (GB): ', sum(volumes))
    print()

def security_group_rules():
    ec2client = boto3.client('ec2')

    response = ec2client.describe_security_groups(GroupNames=['hwdemo'])['SecurityGroups'][0]['IpPermissions']
    print('Port    Inbound IP Address Ranges(s)')
    print('----  -------------------------------')
    for i in response:
        print(i['FromPort'], end='   ')
        print([x['CidrIp'] for x in i['IpRanges']])

def main(name):

    instance_protect(name)
    ebs_profile()
    security_group_rules()

if __name__ == '__main__':

    name = 'atinn'
    main(name)