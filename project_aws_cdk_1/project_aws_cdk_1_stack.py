"""
CDK 1 Stack Module
"""

from aws_cdk import (
    Duration,
    Stack,
    aws_sqs as sqs,
    aws_s3 as s3,
    aws_s3_notifications as s3n,
    aws_lambda as lambda_,
    aws_lambda_event_sources as lambda_event_sources,
    aws_sns as sns,
    aws_sns_subscriptions as subs,
    aws_dynamodb as ddb,
    RemovalPolicy
)
from constructs import Construct


STR_PART = "project-aws-cdk-3-3"


class ProjectAwsCdk1Stack(Stack):
    """
    CDK 1 Stack
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # SQS example
        self.sqs_example(STR_PART)

        # SNS example
        self.sns_example(STR_PART)

        # MY TEST
        # self.my_test_s3(STR_PART)
        # self.my_test_ddb(STR_PART)

    def sqs_example(self, str_part):
        """
        SQS Example

        :param str_part:
        :return:
        """

        # Create SQS queue
        queue_1 = sqs.Queue(
            self,
            f'sqs-queue-id-{str_part}',
            queue_name=f'sqs-queue-{str_part}',
            visibility_timeout=Duration.seconds(300),
        )

        # Create Lambda Layer
        lambda_layer_1 = lambda_.LayerVersion(
            self,
            f'sqs-lambda_layer-id-{str_part}',
            code=lambda_.Code.from_asset('lambda_layers/lambda_layer_sqs.zip'),
            compatible_runtimes=[lambda_.Runtime.PYTHON_3_9],
            layer_version_name=f'sqs-lambda_layer-{str_part}',
            compatible_architectures=[lambda_.Architecture.ARM_64]

        )

        # Create Lambda function
        lambda_1 = lambda_.Function(
            self,
            f'sqs-lambda-id-{str_part}',
            function_name=f'sqs-lambda-{str_part}',
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler='lambda_handler_sqs.lambda_handler',
            code=lambda_.Code.from_asset('lambda'),
            layers=[lambda_layer_1],
            architecture=lambda_.Architecture.ARM_64
        )
        # Create Event Source
        sqs_event_source = lambda_event_sources.SqsEventSource(queue_1)
        # Add SQS Event Source to Lambda function
        lambda_1.add_event_source(sqs_event_source)

        # Create S3 Bucket
        bucket_1 = s3.Bucket(
            self,
            f'sqs-bucket-id-{str_part}',
            bucket_name=f'sqs-bucket-{str_part}',
            versioned=True
        )
        # Add S3 event notification to trigger Lambda via SQS for inserting new object
        bucket_1.add_event_notification(
            s3.EventType.OBJECT_CREATED,
            s3n.SqsDestination(queue_1)
        )
        # Add S3 event notification to trigger lambda via SQS for object deletion
        bucket_1.add_event_notification(
            s3.EventType.OBJECT_REMOVED,
            s3n.SqsDestination(queue_1)
        )
        # Grant S3 permission to Lambda
        bucket_1.grant_read(lambda_1)

    def sns_example(self, str_part):
        """
        SNS Example

        :param str_part:
        :return:
        """

        # Create Lambda Layer
        lambda_layer_1 = lambda_.LayerVersion(
            self,
            f'sns-lambda_layer-id-{str_part}',
            code=lambda_.Code.from_asset('lambda_layers/lambda_layer_sns.zip'),
            compatible_runtimes=[lambda_.Runtime.PYTHON_3_9],
            layer_version_name=f'sns-lambda_layer-{str_part}',
            compatible_architectures=[lambda_.Architecture.ARM_64]

        )

        # Create Lambda function
        lambda_1 = lambda_.Function(
            self,
            f'sns-lambda-id-{str_part}',
            function_name=f'sns-lambda-{str_part}',
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler='lambda_handler_sns.lambda_handler',
            code=lambda_.Code.from_asset('lambda'),
            layers=[lambda_layer_1],
            architecture=lambda_.Architecture.ARM_64
        )

        # Define the SNS topic
        sns_topic_1 = sns.Topic(
            self,
            f'sns-topic-id-{str_part}',
            display_name=f'sns-display-topic-{str_part}',
            topic_name=f'sns-topic-{str_part}',
            # fifo=True,
        )
        # Subscribe the Lambda function to the SNS topic
        sns_topic_1.add_subscription(subs.LambdaSubscription(lambda_1))

        # Create S3 Bucket
        bucket_1 = s3.Bucket(
            self,
            f'sns-bucket-id-{str_part}',
            bucket_name=f'sns-bucket-{str_part}',
            versioned=True
        )
        # Add SNS event notification to trigger Lambda via SNS for inserting new object
        s3_notification_1 = s3n.SnsDestination(sns_topic_1)
        bucket_1.add_event_notification(
            s3.EventType.OBJECT_CREATED,
            s3_notification_1
        )
        # Add SNS event notification to trigger lambda via SNS for object deletion
        bucket_1.add_event_notification(
            s3.EventType.OBJECT_REMOVED,
            s3_notification_1
        )

    def my_test_s3(self, str_part):
        """
        TEST 3

        :param str_part:
        :return:
        """

        # Create S3 Bucket
        s3.Bucket(
            self,
            f'test-bucket-id-{str_part}',
            bucket_name=f'test-bucket-{str_part}',
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY,  # Removes the bucket when the stack is deleted
            # block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            public_read_access=True,  # Allow public read access
            block_public_access=s3.BlockPublicAccess(
                block_public_acls=False,
                ignore_public_acls=False,
                block_public_policy=False,
                restrict_public_buckets=False
            )  # This disables blocking
        )

    def my_test_ddb(self, str_part):
        """
        TEST DDB

        :param str_part:
        :return:
        """

        ddb.Table(
            self,
            f'table-id-{str_part}',
            table_name=f"table-{str_part}",
            partition_key=ddb.Attribute(
                name="id",
                type=ddb.AttributeType.STRING
            ),
            billing_mode=ddb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY  # Removes the ddb table when the stack is deleted
        )
