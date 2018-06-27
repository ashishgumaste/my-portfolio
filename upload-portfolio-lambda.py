import boto3
from botocore.client import Config
from io import BytesIO
import zipfile
import mimetypes

def lambda_handler(event, context):
    s3 = boto3.resource('s3')
    sns = boto3.resource('sns')
    topic = sns.Topic('arn:aws:sns:us-east-1:592700788974:deployPortfolioTopic')

    try:
        portfolio_bucket = s3.Bucket('portfolio.ashishgumaste.name')
        build_bucket = s3.Bucket('portfoliobuild.ashishgumaste.name')

        portfolio_zip = BytesIO()
        build_bucket.download_fileobj('portfolio.zip', portfolio_zip)
        #import zipfile

        with zipfile.ZipFile(portfolio_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                portfolio_bucket.upload_fileobj(obj, nm,
                    ExtraArgs={'ContentType':mimetypes.guess_type(nm)[0]})
                portfolio_bucket.Object(nm).Acl().put(ACL='public-read')

        print ("Job Done!")
        topic.publish(Subject="Portfolio Deployed", Message="Portfolio deployed successfully")
    except:
        topic.publish(Subject="Portfolio Deployment failed", Message="The Portfolio was not deployed Successfully")
        raise
    return 'Hello from Lambda'
