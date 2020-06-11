import botocore
import boto3
import json
import cfnresponse
import os
import sys

def lambda_handler(event, context):
    try:
        client = boto3.client('events')
        bus, rule = os.environ.get('bus_rule').split('|')
        rule_config = client.describe_rule(Name=rule, EventBusName=bus)
        event_pattern = json.loads(rule_config['EventPattern'])
        event_pattern['detail']['payload']['image']['id'] = [{ 'exists': True }]
        rule_config['EventPattern'] = json.dumps(event_pattern)
        del rule_config['Arn']
        del rule_config['ResponseMetadata']
        response = client.put_rule(**rule_config)
        cfnresponse.send(event, context, cfnresponse.SUCCESS, response, event["RequestId"])
    except botocore.exceptions.ClientError as exception:
        cfnresponse.send(event, context, cfnresponse.FAILED, exception.response['Error'], event["RequestId"])
    except Exception as exception:
        print(sys.exc_info())
        cfnresponse.send(event, context, cfnresponse.FAILED, {}, event["RequestId"])
