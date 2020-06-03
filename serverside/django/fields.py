from django.db import models


""" Notes

The S3Field stores 3 keys of imformation to allow
for maximum flexibility, a `key` and `bucket` are naturally
needed, but we also included a `location` key, so that
even in the circumstance you may be using different
object storage platforms, we have got you covered!
"""


class S3FieldObject:

    def __init__(self, location: str, bucket: str = None, key: str = None):
        self.location = location
        self.bucket = bucket
        self.key = key

    @property
    def repr(self) -> str:
        if self.location is None:
            return None
        return f"{self.location}::{self.bucket}::{self.key}"


class S3Field(models.CharField):

    def __init__(self, *args, **kwargs):
        kwargs["max_length"] = 255  # TODO- will this be long enough?
        kwargs["blank"] = False
        super(S3Field, self).__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection, context):
        location = None
        bucket = None
        key = None
        if value is not None:
            try:
                location, bucket, key = value.split("::")
            except ValueError:
                pass
        return S3FieldObject(location=location, bucket=bucket, key=key)

    def get_prep_value(self, value):
        if value is None:
            return None
        elif isinstance(value, str):
            raise ValueError("Custom Field <S3Field> should initialize with object of type <S3FieldObject>.")
        elif isinstance(value, S3FieldObject):
            return value.repr
        else:
            print("VALUE: ", value)
            raise Exception("CharField handling a non-str value??")
