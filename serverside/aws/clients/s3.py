import typing as ty
import boto3


class S3Client:

    def __init__(
        self,
        endpoint_url: str,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        use_ssl: bool = True
    ):
        self._client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            use_ssl=use_ssl
        )
        self._resource = boto3.resource(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            use_ssl=use_ssl
        )

    @property
    def client(self):
        return self._client

    @property
    def resource(self):
        return self._resource

    def create_bucket_if_not_exists(self, bucket: str, acl: str, on_create: ty.Callable = None):
        try:
            self._client.head_bucket(Bucket=bucket)
        except Exception as err:
            print("err: NEED TO FIND OUT WHAT ERROR THIS IS TO SPECIFICALLY CATCH!!!", err)
            self._client.create_bucket(ACL=acl, Bucket=bucket)
            if on_create is not None:
                on_create()

    def generate_presigned_url(
        self,
        bucket: str,
        key: str,
        content_type: str,
        method: str,
        expires_in: int = 3600
    ) -> str:
        assert method.upper() in ["GET", "PUT"]
        presigned_url = self._client.generate_presigned_url(
            f"{method.lower()}_object",
            Params={
                "Key": key,
                "Bucket": bucket,
                "ContentType": content_type
            },
            ExpiresIn=expires_in,
            HttpMethod=method.upper()
        )
        return presigned_url

    def urlify(self, url: str, bucket: str, key: str, ssl: bool = True, local: bool = False) -> str:
        """ Local supports operations through Localstack and through Minio """
        return f"http{'s' if ssl is True else ''}://{bucket}{'.' if local is True else '/'}{key}"

    def upload_bytes(
        self,
        location: str,
        bucket: str,
        body: bytes,
        content_type: str,
        key: str = None
    ) -> None:
        try:
            body.seek(0)
        except Exception:
            pass
        self._client.put_object(
            Bucket=bucket,
            Key=key,
            Body=body,
            ContentType=content_type
        )

    def copy(self, from_bucket: str, from_key: str, to_bucket: str, to_key: str) -> None:
        self._client.copy_object(
            Bucket=to_bucket,
            Key=to_key,
            CopySource=f"{from_bucket}/{from_key}"
        )

    def get_object(self, bucket: str, key: str):
        return self._client.get_object(Bucket=bucket, Key=key)["Body"].read()
