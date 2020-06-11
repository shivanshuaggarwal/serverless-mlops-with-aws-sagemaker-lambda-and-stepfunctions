# Serverless MLOps with AWS SageMaker, Lambda and StepFunctions
To run this demo, clone this repo to your SageMaker notebook instance and then go through the following notebooks in order:
* `Admin-Setup.ipynb`: Creates the required S3 Buckets, Docker Image and IAM Roles.
* `SageMaker-Setup.ipynb`: Creates and runs SageMaker Processing, Training and Hosting using AWS Lambda.
* `Workflow-Setup.ipynb`: Creates the StepFunction workflow that automates all steps in SageMaker-Setup.ipynb

![Workflow Graph](/README-IMAGES/stepfunctions_graph.png)