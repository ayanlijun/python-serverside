import typing as ty
from rest_framework import serializers
import django
from django.db import models
from ._utils import recursive_camel2snake


async def django_create(info, input: ty.Dict, Model: models.Model, gen_uid: ty.Callable) -> ty.Dict:

    snake_input = recursive_camel2snake(input)
    for field in Model._meta.get_fields():
        if isinstance(field, models.fields.related.ForeignKey):
            fk_id = snake_input.pop(f"{field.name}_id")
            snake_input[field.name] = fk_id

    response = {"error": False, "message": "Create Successfull!", "node": None}
    try:
        def create(self, validated_data):
            attrs_to_set = {}
            for attr, value in validated_data.items():
                if isinstance(getattr(Model, attr), django.db.models.fields.related_descriptors.ManyToManyDescriptor):
                    vals = validated_data.pop(attr, None)
                    attrs_to_set[attr] = vals
                elif isinstance(getattr(Model, attr), django.db.models.fields.related_descriptors.ForwardManyToOneDescriptor):
                    pass
                elif isinstance(getattr(Model, attr), django.db.models.query_utils.DeferredAttribute):
                    pass
                else:
                    print("instance not caught?")
                    pass
            instance = Model.objects.create(**validated_data)
            for attr, value in attrs_to_set.items():
                setattr(instance, attr, value)
            instance.save()
            return instance

        def update(self, instance, validated_data):
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            return instance

        def get_updated(self, obj):
            return obj.updated.timestamp()

        def get_created(self, obj):
            return obj.updated.timestamp()

        serializer = type("Serializer", (serializers.ModelSerializer,), {
            **dict(create=create, update=update, get_updated=get_updated, get_created=get_created),
            "Meta": type(Model.__name__, (), {
                "model": Model,
                "fields": "__all__"
            }),
            "updated": serializers.SerializerMethodField(),
            "created": serializers.SerializerMethodField(),
        })(data={"id": gen_uid(), **snake_input})
        if serializer.is_valid():
            instance = serializer.save()
            return {**response, "node": instance}
        else:
            raise Exception(f"Serializer Error: {serializer.errors}")
    except Exception as err:
        return {**response, "error": True, "message": f"Create Error: {err}"}
