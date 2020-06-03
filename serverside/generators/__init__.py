import uuid

from .identicon import Identicon


gen_uid = lambda: str(uuid.uuid4())


__all__ = [
    "Identicon",
    "gen_uid"
]
