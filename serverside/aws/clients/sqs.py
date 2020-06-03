import typing as ty
import json
import boto3


class SQSClient:

    def __init__(
        self,
        endpoint_url: str,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        use_ssl: bool = True,
    ):
        self._client = boto3.client(
            "sqs",
            endpoint_url=endpoint_url,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            use_ssl=use_ssl
        )

    def push_to_queue(self, url: str, message: ty.Dict, message_attributes: ty.Dict = None) -> None:
        assert isinstance(message, dict)
        attrs = {"QueueUrl": url, "MessageBody": json.dumps(message)}
        if message_attributes is not None:
            attrs["MessageAttributes"] = message_attributes
        try:
            self._client.send_message(**attrs)
        except Exception as err:  # TODO! A specific exception needs to be caught here for queue not existing
            print("SQS EXCEPTION (PUSH TO QUEUE): ", err)

    def try_create_queue(self, name: str) -> str:  # returns url if created
        try:
            return self._client.create_queue(QueueName=name).get("QueueUrl")
        except Exception as err:  # TODO! A specific exception needs to be caught here for queue not existing
            print("SQS EXCEPTION (TRY CREATE QUEUE): ", err)
            return self._client.get_queue_url(QueueName=name).get("QueueUrl")
