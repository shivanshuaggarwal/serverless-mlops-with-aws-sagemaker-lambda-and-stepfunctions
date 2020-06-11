import boto3
import logging
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)
sm_client = boto3.client('sagemaker')

def lambda_handler(event, context):

    if ('JOB_NAME' in event):
        job_name = event['JOB_NAME']

    else:
        raise KeyError('JOB_NAME key not found in function input!'+
                      ' The input received was: {}.'.format(json.dumps(event)))

    #Query boto3 API to check training status.
    try:
        response = sm_client.describe_training_job(TrainingJobName=job_name)
        logger.info("Training job:{} has status:{}.".format(job_name,
            response['TrainingJobStatus']))

    except Exception as e:
        response = ('Failed to read training status!'+ 
                    ' The training job may not exist or the job name may be incorrect.'+ 
                    ' Check SageMaker to confirm the job name.')
        print(e)
        print('{} Attempted to read job name: {}.'.format(response, job_name))


    return {
        'statusCode': 200,
        'TrainingJobStatus': response['TrainingJobStatus']
    }