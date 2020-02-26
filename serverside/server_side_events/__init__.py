import typing as ty
import ujson
import psutil
import asyncio
from aiohttp_sse import sse_response
from datetime import datetime


class ServerSideEvents:

    """
    Note: This helper only works with aiohttp handling requests
    """

    def __init__(self, cors_headers: ty.Dict = None):
        self.cors_headers = cors_headers
        if self.cors_headers is None:
            self.cors_headers = {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Max-Age": "3600",
                "Access-Control-Allow-Headers": "Content-Type, Accept, X-Requested-With, Authorization, device"
            }

    async def get_system_info(self, request):
        loop = request.app.loop
        async with sse_response(request, headers=self.cors_headers) as resp:
            while True:
                await resp.send(ujson.dumps({"data": self.__get_system_info()}), event="systemInfo")
                await asyncio.sleep(3, loop=loop)
        return resp

    def __get_system_info(self) -> ty.Dict:
        svmem = psutil.virtual_memory()
        net_io = psutil.net_io_counters()
        return {
            "time": datetime.utcnow().strftime("%H:%M:%S"),
            "cpu": {
                "physical_cores": psutil.cpu_count(logical=False),
                "logical_cores": psutil.cpu_count(logical=True),
                "cpu_usage": psutil.cpu_percent(),
                "core_usage": [p for p in psutil.cpu_percent(percpu=True)]
            },
            "memory": {
                "total": self.__get_size(svmem.total),
                "available": self.__get_size(svmem.available),
                "used": self.__get_size(svmem.used),
                "percentage": svmem.percent
            },
            "net": {
                "sent": self.__get_size(net_io.bytes_sent),
                "recv": self.__get_size(net_io.bytes_recv)
            }
        }

    def __get_size(self, bytes, suffix="B") -> str:
        """
        Scale bytes to its proper format
        e.g:
            1253656 => '1.20MB'
            1253656678 => '1.17GB'
        """
        factor = 1024
        for unit in ["", "K", "M", "G", "T", "P"]:
            if bytes < factor:
                return f"{bytes:.2f}{unit}{suffix}"
            bytes /= factor
