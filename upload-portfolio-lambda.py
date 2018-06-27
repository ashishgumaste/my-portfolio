import boto3
from botocore.client import Config
from io import BytesIO
import zipfile
import mimetypes

def lambda_handler(event, context):
    s3 = boto3.resource('s3')
    sns = boto3.resource('sns')
    topic = sns.Topic('arn:aws:sns:us-east-1:592700788974:deployPortfolioTopic')

    location = {
        "bucketName":'portfoliobuild.ashishgumaste.name',
        "objectKey": 'portfolio.zip'
    }

    try:
        job = event.get("CodePipeline.job")

        if job:
            for artifact in job["data"]["inputArtifacts"]:
                if artifact["name"] == "MyAppBuild":
                    location = artifact["location"]["s3Location"]

        print ("Building portfolio from" + str(location))

        portfolio_bucket = s3.Bucket('portfolio.ashishgumaste.name')
        build_bucket = s3.Bucket(location["bucketName"])

        portfolio_zip = BytesIO()
        build_bucket.download_fileobj(location["objectKey"], portfolio_zip)

        with zipfile.ZipFile(portfolio_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                portfolio_bucket.upload_fileobj(obj, nm,
                    ExtraArgs={'ContentType':mimetypes.guess_type(nm)[0]})
                portfolio_bucket.Object(nm).Acl().put(ACL='public-read')

        print ("Job Done!")
        topic.publish(Subject="Portfolio Deployed", Message="Portfolio deployed successfully")
        if job:
            codepipeline = boto3.client('codepipeline')
            codepipeline.put_job_success_result(jobId=job["id"])
    except:
        topic.publish(Subject="Portfolio Deployment failed", Message="The Portfolio was not deployed Successfully")
        raise
    return 'Hello from Lambda'
