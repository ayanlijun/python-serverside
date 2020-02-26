from datetime import datetime
from ariadne import ScalarType


datetime_scalar = ScalarType("Datetime")


@datetime_scalar.serializer
def serialize_datetime(value):
    return value.timestamp()


@datetime_scalar.value_parser
def parse_datetime_value(value):
    assert value is not None, "There was a null value passed into a datetime creator"
    return datetime.utcfromtimestamp(value)


@datetime_scalar.literal_parser
def parse_datetime_literal(ast):
    value = float(ast.value)
    return parse_datetime_value(value)
