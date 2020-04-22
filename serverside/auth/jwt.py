import typing as ty
from datetime import datetime
import jwt


class JWTAuth:

    def __init__(self, secret_key: str, encode_algorithm: str, decode_algorithms: ty.List) -> str:
        self.secret_key = secret_key
        self.encode_algorithm = encode_algorithm
        self.decode_algorithms = decode_algorithms

    def encode_jwt(self, payload: ty.Dict, expiration: datetime):
        assert "exp" not in payload
        assert isinstance(expiration, datetime)
        return jwt.encode(
            {**payload, "exp": expiration.timestamp()},
            self.secret_key,
            algorithm=self.encode_algorithm
        ).decode("utf-8")

    def authenticate_jwt(self, token: str) -> tuple:
        """ returns: (<error:bool>, <err_msg:str>, <decoded_jwt>: dict) """
        try:
            decoded = jwt.decode(token, self.secret_key, algorithms=self.decode_algorithms)
            return (True, None, decoded)
        except jwt.exceptions.InvalidSignatureError:
            return (False, "Signature verification failed", None)
        except jwt.exceptions.DecodeError:
            return (False, "Not enough segments in the token.", None)
        except Exception as err:
            return (False, str(err), None)


