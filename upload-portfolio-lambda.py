import json
import boto3
import zipfile
import io
import mimetypes

def lambda_handler(event, context):
    sns = boto3.resource('sns')
    topic = sns.Topic('arn:aws:sns:us-east-1:266214946304:deployPortfolioTopic')
    try:
        s3 = boto3.resource('s3')
        portfolio_bucket = s3.Bucket('portfolio.hamzajav.com')
        build_bucket = s3.Bucket('portfoliobuild.hamzajav.com')
        portfolio_zip = io.BytesIO()
        build_bucket.download_fileobj('portfoliobuild.zip', portfolio_zip)

        with zipfile.ZipFile(portfolio_zip) as myzip:
            for name in myzip.namelist():
                obj = myzip.open(name)
                portfolio_bucket.upload_fileobj(obj, name, ExtraArgs={'ContentType': mimetypes.guess_type(name)[0]})
                portfolio_bucket.Object(name).Acl().put(ACL='public-read')

        topic.publish(Subject='Portfolio Deployed', Message='Portfolio deployed successfully!')

    except:
        topic.publish(Subject='Portfolio Deployment Failed', Message='Portfolio not deployed! An error occurred')
        raise

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
