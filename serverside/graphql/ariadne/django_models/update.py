import typing as ty
from collections import OrderedDict

from rest_framework import serializers
from django.db import models
from ._utils import input2snake_input


async def django_update(
    info,
    Model: models.Model,
    id: str,
    field: str,
    prevUpdated: float,
    input: ty.Dict,
    Serializer: serializers.Serializer = None
) -> ty.Dict:

    fields_needed = []
    for l1i, l1v in enumerate(info.field_nodes):
        if l1v.name.value == field:
            for l2i, l2v in enumerate(l1v.selection_set.selections):
                if l2v.name.value == "node":
                    for l3i, l3v in enumerate(l2v.selection_set.selections):
                        fields_needed.append(l3v.name.value)

    new_declared_fields = OrderedDict()
    for field_name, field_value in Serializer._declared_fields.items():
        if field_name in fields_needed:
            new_declared_fields[field_name] = field_value
    Serializer._declared_fields = new_declared_fields

    snake_input = input2snake_input(Model=Model, input=input)

    response = {"error": False, "message": "Update Successfull!", "node": None}
    try:
        instance = Model.objects.get(id=id)
        assert instance.updated.timestamp() == prevUpdated, "This object has been updated since last got it."

        _before = Serializer(instance).data
        serializer = Serializer(instance, data={**_before, **snake_input}, many=False)
        if serializer.is_valid():
            serializer.save()
            return {**response, "node": serializer.data}
        else:
            return {**response, "error": True, "message": str(serializer.errors)}
    except Model.DoesNotExist:
        return {**response, "error": True, "message": f"The object with id {id} could not be found."}
    except Exception as err:
        return {**response, "error": True, "message": f"Update Error: {err}"}
