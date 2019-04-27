# Copyright (C) 2011-2018 Vas Vasiliadis
# University of Chicago
##
__author__ = 'Vas Vasiliadis <vas@uchicago.edu>'

import sys
import time
import driver
import boto3
import os

"""A rudimentary timer for coarse-grained profiling
"""
class Timer(object):
  def __init__(self, verbose=True):
    self.verbose = verbose

  def __enter__(self):
    self.start = time.time()
    return self

  def __exit__(self, *args):
    self.end = time.time()
    self.secs = self.end - self.start
    if self.verbose:
      print("Total runtime: {0:.6f} seconds".format(self.secs))

if __name__ == '__main__':
  # Call the AnnTools pipeline
  if len(sys.argv) > 1:
    with Timer():
      driver.run(sys.argv[1], 'vcf')

    # taken from https://qiita.com/hengsokvisal/items/329924dd9e3f65dd48e7
    s3_client = boto3.client('s3')
    ID = sys.argv[2]
    filename = sys.argv[3]
    path = sys.argv[4]
    prefix = filename.partition('.')[0]

    # upload the annot.vcf
    s3_client.upload_file('../jobs/{}/{}.annot.vcf'.format(ID, prefix), 'gas-results', '{}~{}.annot.vcf'.format(path, prefix))

    # upload the log file
    s3_client.upload_file('../jobs/{}/{}.vcf.count.log'.format(ID, prefix), 'gas-results', '{}~{}.vcf.count.log'.format(path, prefix))

    # create new UUID folder in ./jobs
    delete_folder = 'rm -r ../jobs/{}'.format(ID)
    os.system(delete_folder)

  else:
    print("A valid .vcf file must be provided as input to this program.")