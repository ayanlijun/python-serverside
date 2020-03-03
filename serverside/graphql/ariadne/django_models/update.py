import typing as ty
from rest_framework import serializers
import django
from django.db import models
from ._utils import recursive_camel2snake


async def django_update(info, Model: models.Model, id: str, prevUpdated: float, input: ty.Dict) -> ty.Dict:
    snake_input = recursive_camel2snake(input)
    for field in Model._meta.get_fields():
        if isinstance(field, models.fields.related.ForeignKey):
            try:
                fk_id = snake_input.pop(f"{field.name}_id")
                snake_input[field.name] = fk_id
            except KeyError:
                continue  # Foreign key wasn't supplied to be updated

    response = {"error": False, "message": "Update Successfull!", "node": None}
    try:
        instance = Model.objects.get(id=id)
        assert instance.updated.timestamp() == prevUpdated, "This object has been updated since last got it."

        def create(self, validated_data):
            instance = Model.objects.create(**validated_data)
            instance.save()
            return instance

        def update(self, instance, validated_data):
            for attr, value in validated_data.items():
                if isinstance(getattr(Model, attr), django.db.models.fields.related_descriptors.ManyToManyDescriptor):
                    vals = validated_data.pop(attr, None)
                    getattr(instance, attr).set(vals)
                elif isinstance(getattr(Model, attr), django.db.models.fields.related_descriptors.ForwardManyToOneDescriptor):
                    pass
                elif isinstance(getattr(Model, attr), django.db.models.query_utils.DeferredAttribute):
                    pass
                else:
                    print("instance not caught?")
                    pass
                setattr(instance, attr, value)
            instance.save()
            return instance

        def get_updated(self, obj):
            return obj.updated.timestamp()

        def get_created(self, obj):
            return obj.updated.timestamp()

        Serializer = type("Serializer", (serializers.ModelSerializer,), {
            **dict(create=create, update=update, get_updated=get_updated, get_created=get_created),
            "Meta": type(Model.__name__, (), {
                "model": Model,
                "fields": "__all__"
            }),
            "updated": serializers.SerializerMethodField(),
            "created": serializers.SerializerMethodField(),
        })
        before = Serializer(instance).data
        serializer = Serializer(instance, data={**before, **snake_input})
        if serializer.is_valid():
            instance = serializer.save()
            return {**response, "node": instance}
        else:
            print(serializer.errors)
    except Model.DoesNotExist:
        return {**response, "error": True, "message": f"The object with id {id} could not be found."}
    except Exception as err:
        return {**response, "error": True, "message": f"Update Error: {err}"}
