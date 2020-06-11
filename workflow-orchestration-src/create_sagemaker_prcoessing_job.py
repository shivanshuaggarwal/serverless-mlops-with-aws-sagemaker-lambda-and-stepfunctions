import boto3
sagemaker_boto3 = boto3.client('sagemaker')

def lambda_handler(event, context):
    DATA_SOURCE = event["DATA_SOURCE"]
    BUCKET = event["BUCKET"]
    WORKFLOW_DATE_TIME = event["WORKFLOW_DATE_TIME"]
    SOURCE_CODE_PREFIX = event["SOURCE_CODE_PREFIX"]

    # Output data paths
    train_prefix = "{}/data/train".format(WORKFLOW_DATE_TIME)
    val_prefix = "{}/data/validation".format(WORKFLOW_DATE_TIME)
    test_prefix = "{}/data/test".format(WORKFLOW_DATE_TIME)

    s3_train_path = 's3://{}/{}'.format(BUCKET, train_prefix)
    s3_valid_path = 's3://{}/{}'.format(BUCKET, val_prefix)
    s3_test_path = 's3://{}/{}'.format(BUCKET, test_prefix)

    response = sagemaker_boto3.create_processing_job(
        ProcessingInputs = [
            {'InputName': 'input-1',
             'S3Input': {'S3Uri': DATA_SOURCE,
                         'LocalPath': '/opt/ml/processing/input',
                         'S3DataType': 'S3Prefix',
                         'S3InputMode': 'File',
                         'S3DataDistributionType': 'ShardedByS3Key',
                         'S3CompressionType': 'None'
                        }
            },
            {'InputName': 'code',
             'S3Input': {'S3Uri': "s3://{}/{}/{}".format(BUCKET, SOURCE_CODE_PREFIX, event["ENTRY_POINT_SCRIPT"]),
                         'LocalPath': '/opt/ml/processing/input/code',
                         'S3DataType': 'S3Prefix',
                         'S3InputMode': 'File',
                         'S3DataDistributionType': 'FullyReplicated',
                         'S3CompressionType': 'None'
                        }
            }
        ],
        ProcessingOutputConfig = {
            'Outputs': [{'OutputName': 'train',
                         'S3Output': {'S3Uri': s3_train_path,
                                      'LocalPath': '/opt/ml/processing/train',
                                      'S3UploadMode': 'EndOfJob'
                                     }
                        },
                        {'OutputName': 'valid',
                         'S3Output': {'S3Uri': s3_valid_path,
                                      'LocalPath': '/opt/ml/processing/validation',
                                      'S3UploadMode': 'EndOfJob'
                                     }
                        },
                        {'OutputName': 'test',
                         'S3Output': {'S3Uri': s3_test_path,
                                      'LocalPath': '/opt/ml/processing/test',
                                      'S3UploadMode': 'EndOfJob'
                                     }
                        }]
        },
        ProcessingJobName = event["JOB_NAME"],
        ProcessingResources = {'ClusterConfig': {'InstanceCount': event["INSTANCE_COUNT"],
                                                 'InstanceType': event["INSTANCE_TYPE"],
                                                 'VolumeSizeInGB': event["VOLUME_SIZE_GB"]
                                                }
                              },
        StoppingCondition = {'MaxRuntimeInSeconds': 86400},
        AppSpecification = {'ImageUri': event["TRAINING_IMAGE"],
                            'ContainerArguments':  ['--train-test-split-ratio', '0.2'], 
                            'ContainerEntrypoint': ['python3', 
                                                    '/opt/ml/processing/input/code/'+event["ENTRY_POINT_SCRIPT"]
                                                   ]
                           },
        RoleArn = event["ROLE_ARN"]
    )
    return event
    