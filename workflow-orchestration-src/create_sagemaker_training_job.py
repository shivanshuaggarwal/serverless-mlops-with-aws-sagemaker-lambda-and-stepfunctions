import boto3
import os
sagemaker_boto3 = boto3.client('sagemaker')

def lambda_handler(event, context):
    """ Creates a SageMaker training job
    Args:
        TRAINING_JOB_NAME (string): name for training job.
        TRAINING_DATA (string): Path to training datasets directory on S3.
        TESTING_DATA (string): Path to testing datasets directory on S3.
        SOURCE_CODE (string): Path to source-code directory on S3 (tarball).
        ENTRY_POINT_SCRIPT (string): Name of the entry point script for model training.
        TRAINING_IMAGE (string): ECR image that will host model training.
        ROLE_ARN (string): IAM Role to allow the runtime resource to call SageMaker.
        OUTPUT_ARTIFACTS_PATH (string): Path to save model artifacts on S3.
    Returns
        (None)
    """

    TRAINING_JOB_NAME = event['TRAINING_JOB_NAME']
    TRAINING_DATA = event['TRAINING_DATA']
    TESTING_DATA = event['TESTING_DATA']
    SOURCE_CODE = event['SOURCE_CODE']
    ENTRY_POINT_SCRIPT = event['ENTRY_POINT_SCRIPT']
    TRAINING_IMAGE = event['TRAINING_IMAGE']
    ROLE_ARN = event['ROLE_ARN']
    OUTPUT_ARTIFACTS_PATH = event['OUTPUT_ARTIFACTS_PATH']
    INSTANCE_TYPE = event['INSTANCE_TYPE']
    INSTANCE_COUNT = event['INSTANCE_COUNT']
    VOLUME_SIZE_GB = event['VOLUME_SIZE_GB']
    PROCESSING_JOB_NAME = event['PROCESSING_JOB_NAME']

    try:
        response = sagemaker_boto3.create_training_job(
            TrainingJobName=TRAINING_JOB_NAME,
            HyperParameters={
                'n_estimators': '300',
                'min_samples_leaf': '3',
                #'features': 'CRIM ZN INDUS CHAS NOX RM AGE DIS RAD TAX PTRATIO B LSTAT',
                #'target': 'PRICE',
                'sagemaker_program': ENTRY_POINT_SCRIPT,
                'sagemaker_submit_directory': SOURCE_CODE      
            },
            AlgorithmSpecification={
                'TrainingImage': TRAINING_IMAGE,
                'TrainingInputMode': 'File',
                'MetricDefinitions': [
                    {'Name': 'median-AE', 'Regex': 'AE-at-50th-percentile: ([0-9.]+).*$'},
                ]
            },
            RoleArn=ROLE_ARN,
            InputDataConfig=[
                {
                    'ChannelName': 'train',
                    'DataSource': {
                        'S3DataSource': {
                            'S3DataType': 'S3Prefix',
                            'S3Uri': TRAINING_DATA,
                            'S3DataDistributionType': 'FullyReplicated',
                        }
                    }
                },
                {
                    'ChannelName': 'test',
                    'DataSource': {
                        'S3DataSource': {
                            'S3DataType': 'S3Prefix',
                            'S3Uri': TESTING_DATA,
                            'S3DataDistributionType': 'FullyReplicated',
                        }
                    }
                },
            ],
            OutputDataConfig={'S3OutputPath': OUTPUT_ARTIFACTS_PATH},
            ResourceConfig={
                'InstanceType': INSTANCE_TYPE,
                'InstanceCount': INSTANCE_COUNT,
                'VolumeSizeInGB': VOLUME_SIZE_GB
            },
            StoppingCondition={'MaxRuntimeInSeconds': 86400},
            EnableNetworkIsolation=False
        )
        print(response)
    except Exception as e:
        print(e)
        print('Unable to create model.')
        raise(e)