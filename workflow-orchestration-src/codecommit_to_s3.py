import boto3
import os
import mimetypes
import tarfile
import io

def lambda_handler(event, context):
    """ Pulls AWS Glue and SageMaker source code from CodeCommit and writes it to S3.
    This funciton creates a tarball of the SageMaker scripts before sending to S3 since
    SageMaker training jobs expect code to be in a tarball on S3.
    """
    # target bucket
    bucket = boto3.resource('s3').Bucket(event['s3BucketName'])

    # source codecommit
    codecommit = boto3.client('codecommit', region_name=event['codecommitRegion'])
    repository_name = event['repository']
    
    # First create a tar ball with sagemaker scripts to S3 with name source.dir.tar.gz
    buf = io.BytesIO()
    with tarfile.open('sourcedir', mode="w:gz", fileobj=buf) as tar:
        # Reads each file in the branch and uploads it to the s3 bucket
        for blob in get_blob_list(codecommit, repository_name, event['branch'], event['repository_sagemaker_key']):
            path = blob['path']
            blobId = blob['blobId']
            content = (codecommit.get_blob(repositoryName=repository_name, blobId=blobId))['content']
            tarinfo = tarfile.TarInfo(path)
            tarinfo.size = len(content)
            tar.addfile(tarinfo, io.BytesIO(content))
    # close tar file
    tarobject = buf.getvalue()
    # put tar ball in s3
    s3BucketKey = '{}/{}'.format(event['s3BucketKey'], 'sourcedir.tar.gz')
    bucket.put_object(Body=(tarobject), Key=s3BucketKey)

    
    # Sagemaker Processing.
    for blob in get_blob_list(codecommit, repository_name, event['branch'], event['repository_sm_processing_key']):
        path = blob['path']
        blobId=blob['blobId']
        content = (codecommit.get_blob(repositoryName=repository_name, blobId=blobId))['content']
        s3BucketKey = '{}/{}'.format(event['s3BucketKey'], path)
        bucket.put_object(Body=(content), Key=s3BucketKey)
    return('SUCCESS')            


def get_blob_list(codecommit, repository, branch, path):
    """ Returns a list of a all files in a CodeCommit branch
    """
    response = codecommit.get_differences(
            repositoryName=repository,
            afterCommitSpecifier=branch,
            afterPath=path
            )

    blob_list = [difference['afterBlob'] for difference in response['differences']]
    while 'nextToken' in response:
        response = codecommit.get_differences(
                repositoryName=repository,
                afterCommitSpecifier=branch,
                nextToken=response['nextToken']
                )
        blob_list += [difference['afterBlob'] for difference in response['differences']]

    return blob_list    
