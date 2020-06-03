import uuid
import base64
import logging
import typing as ty

import ujson
import redis
import aioredis
from asgiref.sync import async_to_sync

from .exceptions import RedisKeyNotFoundException


class AsyncRedisClient:

    TEST_KEYS = lambda qty: [base64.urlsafe_b64encode(uuid.uuid4().bytes).decode("ascii").strip("=") for i in range(qty)]

    def __init__(self, host: str, port: int, db: int, logger: logging.Logger = None):
        self._redis_host = host
        self._redis_port = port
        self._redis_db = db
        self._logger = logger

    async def async_connect(self):
        self._rclient = await aioredis.create_redis(f"redis://{self._redis_host}:{self._redis_port}", db=self._redis_db)
        if self._logger is not None:
            self._logger.info(f"Redis Client Connected (host={self._redis_host} port={self._redis_port} db={self._redis_db})")
        self._sync_rclient = redis.StrictRedis(host=self._redis_host, port=self._redis_port, db=self._redis_db)

        await self.__preflight_check()
        if self._logger:
            self._logger.info(f"Redis Preflight done (host={self._redis_host} port={self._redis_port} db={self._redis_db})")

    @async_to_sync
    async def async_connect_from_sync(self):
        await self.async_connect()

    async def get(self, key: str):
        res = await self._rclient.get(key)
        if res is None:
            raise RedisKeyNotFoundException
        return res.decode("utf-8")

    async def mget(self, keys: ty.Sequence[str], to_json: bool = False) -> ty.Dict:
        assert isinstance(keys, (list, tuple)), "keys in redis mget must be a iterable"
        assert len(keys) < 20, "too many keys to mget at once"

        values = await self._rclient.mget(*keys)
        results = {}
        for key, value in zip(keys, values):
            if value is None:
                results[key] = value
                continue
            if to_json is True:
                results[key] = ujson.loads(value.decode("utf-8"))
            else:
                results[key] = value.decode("utf-8")
        return results

    async def set(self, key: str, value: str, expire: int = 0):
        assert isinstance(value, str), "Please convert the value to a string before using redis.set"
        await self._rclient.set(key, value, expire=expire)

    async def mset(self, mapping: ty.Dict = {}, expire: int = 0, *args):
        assert len(mapping.keys()) + len(args) < 20, "Max keys for mset is 20!"
        if expire > 0:
            for k, v in mapping.items():
                await self.set(key=k, value=v, expire=expire)
        else:
            for k, v in mapping.items():
                args = args + (k, v)
            await self._rclient.mset(*args)

    async def mexpire(self, keys: ty.List[str], expire: int):
        # TODO? Is there a way to directly run redis query strings?
        try:
            await self._rclient.command("MULTI\nexpire " + "\nexpire ".join([f"{k} {expire}" for k in keys]) + "\nEXEC")
        except Exception as err:
            if self._logger is not None:
                self._logger.error(str(err))

    async def mdel(self, key: str = None, keys: list = []):
        assert key or keys, "no key to remove from redis"
        assert len(keys) < 20, "Max keys for del is 20!"
        if key:
            await self._rclient.delete(key=key)
        if keys:
            await self._rclient.delete(keys=keys)

    async def __preflight_check(self):
        for key in self._sync_rclient.scan_iter("tests::*"):
            self._sync_rclient.delete(key)
        assert isinstance(self._rclient, aioredis.commands.Redis)
        a, b, c, d = AsyncRedisClient.TEST_KEYS(4)
        await self.set(f"tests::set::{a}", f"{a}")
        assert await self.get(f"tests::set::{a}") == f"{a}"
        await self.mset({f"tests::mset::{b}": f"{b}", f"tests::mset::{c}": f"{c}", f"tests::mset::{d}": f"{d}"})
        mget_res = await self.mget([f"tests::mset::{b}", f"tests::mset::{c}", f"tests::mset::{d}"])
        for i in [(f"tests::mset::{b}", f"{b}"), (f"tests::mset::{c}", f"{c}"), (f"tests::mset::{d}", f"{d}")]:
            try:
                assert mget_res[i[0]] == i[1]
            except KeyError:
                raise Exception("FAILED TO GET KEY FROM LOOKUP!")
        for key in self._sync_rclient.scan_iter("tests::*"):
            self._sync_rclient.delete(key)
