import subprocess
import time

def automate():
    '''Need to be shelled into the correct instance'''

    a=False
    b=False
    c=False

    #start the processess
    a_sub = subprocess.Popen(['sh', '-c', 'cd ./anntools && python run.py ./data/{}'.format('free_1.vcf')])
    b_sub = subprocess.Popen(['sh', '-c', 'cd ./anntools && python run.py ./data/{}'.format('premium_1.vcf')])
    c_sub = subprocess.Popen(['sh', '-c', 'cd ./anntools && python run.py ./data/{}'.format('premium_2.vcf')])


    polls = [a_sub.poll(),b_sub.poll(),c_sub.poll()]

    #while all jobs are still runnning
    while True:
        # all jobs are complete, break
        if all(subs is not None for subs in polls):
            break
        else:
            if a_sub.poll() != None and a == False:
                a = True
                a_time = time.time()
            if b_sub.poll() != None and b == False:
                b = True
                b_time = time.time()
            if c_sub.poll() != None and c == False:
                c = True
                c_time = time.time()


print('free_1.vcf took {} seconds'.format(a_time))
print('premium_1.vcf took {} seconds'.format(b_time))
print('premium_2.vcf took {} seconds'.format(c_time))
