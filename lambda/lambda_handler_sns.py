"""
SNS Module
"""

import json
import logging
import requests
from bs4 import BeautifulSoup as bs

from aws_xray_sdk.core import xray_recorder


logger = logging.getLogger()
logger.setLevel("INFO")


@xray_recorder.capture('lambda_handler')
def lambda_handler(event, context):
    """
    Lambda Handler

    :param event:
    :param context:
    :return:
    """

    logger.info('event: %s - %s', type(event), event)

    # Process SNS
    process_sns(event)

    # Verify Python packages
    verify_python_packages()


def verify_python_packages():
    """
    Verify Python Packages

    :return:
    """

    logger.info('Start testing packages "requests" and "bs4"')
    r = requests.get('https://www.google.com', timeout=30)
    soup = bs(r.text, 'html.parser')
    title = soup.title.string
    logger.info('title: %s', title)
    logger.info('Finished testing packages "requests" and "bs4"')


def process_sns(event):
    """
    Process SNS

    :param event:
    :return:
    """

    logger.info('Start processing messages (SNS)')
    records = event.get('Records', [])
    for record in records:
        event_source = record['eventSource']
        record_sns = record.get('Sns', [])
        if not record_sns:
            continue
        record_sns_subject = record_sns['Subject']
        record_sns_msg = record_sns['Message']
        record_sns_msg_json = json.loads(record_sns_msg)
        sns_records = record_sns_msg_json.get('Records', [])
        for sns_record in sns_records:
            event_name = sns_record['eventName']
            if event_name.startswith('ObjectCreated:'):
                operation = 'CREATED'
            elif event_name.startswith('ObjectRemoved:'):
                operation = 'DELETED'
            else:
                operation = '"UNKNOWN OPERATION"'
            sns_record_s3 = sns_record['s3']
            bucket_name = sns_record_s3['bucket']['name']
            file_name = sns_record_s3['object']['key']
            logger.info('event_source: %s\n'
                        'subject: %s\n'
                        'bucket: %s\n'
                        'file: %s\n'
                        'operation: %s\n'
                        'status: success',
                        event_source, record_sns_subject, bucket_name, file_name, operation)
    logger.info('Finished processing messages (SNS)')
