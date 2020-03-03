import typing as ty
from django.db import models


async def django_delete(info, Model: models.Model, id: str) -> ty.Dict:
    response = {"error": False, "message": "Delete Successfull!"}
    try:
        instance = Model.objects.get(id=id)
        instance.delete()
        return response
    except Model.DoesNotExist:
        return {**response, "error": True, "message": f"The object with id {id} could not be found."}
    except Exception as err:
        return {**response, "error": True, "message": f"Delete Error: {err}"}
    return response
