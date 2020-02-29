import typing as ty
import inflection
from collections import OrderedDict
from rest_framework import serializers
import django
from django.db import models


def recursive_snake2camel(d: ty.Dict):
    new = {}
    for k, v in d.items():
        if isinstance(v, OrderedDict):
            v = recursive_snake2camel(v)
        if isinstance(v, list):
            v = [recursive_snake2camel(i) if isinstance(i, OrderedDict) else i for i in v]
        new[inflection.camelize(k, False)] = v
    return new


def recursive_camel2snake(d: ty.Dict):
    new = {}
    for k, v in d.items():
        if isinstance(v, OrderedDict):
            v = recursive_camel2snake(v)
        if isinstance(v, list):
            v = [recursive_camel2snake(i) if isinstance(i, OrderedDict) else i for i in v]
        new[inflection.underscore(k)] = v
    return new


async def django_get_one(info, Model: models.Model, id: str) -> models.Model:
    fields = info.field_nodes[0].selection_set.selections
    fields = [field.name.value for field in fields]
    camel_query_fields = [i for i in fields if not i.startswith("__")]
    snake_query_fields = [inflection.underscore(field) for field in camel_query_fields]

    regular_fields = []
    foreignkey_fields = []
    foreignkey_fields_to_apply = []
    many2many_fields = []
    many2many_fields_to_apply = []
    many2one_fields = []
    many2one_fields_to_apply = []
    for field in Model._meta.get_fields():
        if isinstance(field, models.fields.related.ForeignKey):
            foreignkey_fields.append(field)
            if field.name in snake_query_fields:
                foreignkey_fields_to_apply.append(field)
        elif isinstance(field, models.fields.related.ManyToManyField):
            many2many_fields.append(field)
            if field.name in snake_query_fields:
                many2many_fields_to_apply.append(field)
        elif isinstance(field, models.fields.reverse_related.ManyToOneRel):
            many2one_fields.append(field)
            if field.name in snake_query_fields:
                many2one_fields_to_apply.append(field)
        elif isinstance(field, models.fields.reverse_related.ManyToManyRel):
            pass
        else:
            regular_fields.append(field.name)

    snake_query_fields = [i for i in snake_query_fields if i in regular_fields]
    query_fields = regular_fields + [i.name for i in foreignkey_fields_to_apply]
    query = Model.objects.only(*query_fields)

    for foreignkey_field in foreignkey_fields_to_apply:
        query = query.select_related(foreignkey_field.name)
    for many2one_field in many2one_fields_to_apply:
        query = query.prefetch_related(
            models.Prefetch(
                many2one_field.name,
                queryset=many2one_field.related_model.objects.all(),
                to_attr=f"m2o_{many2one_field.name}"
            )
        )
    for many2many_field in many2many_fields_to_apply:
        query = query.prefetch_related(
            models.Prefetch(
                many2many_field.name,
                queryset=many2many_field.related_model.objects.all(),
                to_attr=f"m2m_{many2many_field.name}"
            )
        )

    query = query.get(id=id)
    return query


async def django_get_many(info, Model: models.Model, field: str, kwargs: ty.Dict = {}) -> ty.Dict:
    print("HERE!!!!!")
    first = kwargs.pop("first", None)
    after = kwargs.pop("after", None)
    before = kwargs.pop("before", None)
    sortBy = kwargs.pop("sortBy", None)
    sortDirection = kwargs.pop("sortDirection", None)
    filters = kwargs

    getTotal = False
    getHasNextPage = False
    # getHasPreviousPage = False
    # getStartCursor = False
    # getEndCursor = False

    camel_query_fields = []
    for l1i, l1v in enumerate(info.field_nodes):
        if l1v.name.value == field:
            for l2i, l2v in enumerate(l1v.selection_set.selections):
                if l2v.name.value == "edges":
                    for l3i, l3v in enumerate(l2v.selection_set.selections):
                        if l3v.name.value == "node":
                            for l4i, l4v in enumerate(l3v.selection_set.selections):
                                camel_query_fields.append(l4v.name.value)
                            break
                elif l2v.name.value == "pageInfo":
                    for l3i, l3v in enumerate(l2v.selection_set.selections):
                        if l3v.name.value == "total":
                            getTotal = True
                        elif l3v.name.value == "hasNextPage":
                            getHasNextPage = True
                        elif l3v.name.value == "hasPreviousPage":
                            pass
                            # getHasPreviousPage = True
                        elif l3v.name.value == "startCursor":
                            pass
                            # getStartCursor = True
                        elif l3v.name.value == "endCursor":
                            pass
                            # getEndCursor = True

    camel_query_fields = [i for i in camel_query_fields if not i.startswith("__")]
    snake_query_fields = [inflection.underscore(field) for field in camel_query_fields]

    regular_fields = []
    foreignkey_fields = []
    foreignkey_fields_to_apply = []
    many2many_fields = []
    many2many_fields_to_apply = []
    many2one_fields = []
    many2one_fields_to_apply = []
    for field in Model._meta.get_fields():
        if isinstance(field, models.fields.related.ForeignKey):
            foreignkey_fields.append(field)
            if field.name in snake_query_fields:
                foreignkey_fields_to_apply.append(field)
        elif isinstance(field, models.fields.related.ManyToManyField):
            many2many_fields.append(field)
            if field.name in snake_query_fields:
                many2many_fields_to_apply.append(field)
        elif isinstance(field, models.fields.reverse_related.ManyToOneRel):
            many2one_fields.append(field)
            if field.name in snake_query_fields:
                many2one_fields_to_apply.append(field)
        elif isinstance(field, models.fields.reverse_related.ManyToManyRel):
            print("TODO- THIS NEEDS TO BE HANDLED!!!!")
            pass
        else:
            regular_fields.append(field.name)

    snake_query_fields = [i for i in snake_query_fields if i in regular_fields]
    query_fields = regular_fields + [i.name for i in foreignkey_fields_to_apply]
    query = Model.objects.all().only(*query_fields)  # Efficient as possible

    has_previous_page = False
    # has_next_page = False

    for qfk, qfv in filters.items():
        query = query.filter(**{qfk: qfv})

    if after is not None and before is not None:
        raise Exception("You can't query with both `before` and `after`")

    if after is not None:
        after = after + 1  # So as to start from the idx AFTER the cursor provided
        has_previous_page = True
    else:
        after = 0

    if first is None:
        first = 20

    if before is not None:
        after = before - first

    if sortBy is not None:
        if sortDirection == "desc":
            query = query.order_by(f"-{sortBy}")
        else:
            query = query.order_by(sortBy)

    after = max(after, 0)

    for foreignkey_field in foreignkey_fields_to_apply:
        query = query.select_related(foreignkey_field.name)
    for many2one_field in many2one_fields_to_apply:
        query = query.prefetch_related(
            models.Prefetch(
                many2one_field.name,
                queryset=many2one_field.related_model.objects.all(),
                to_attr=f"m2o_{many2one_field.name}"
            )
        )
    for many2many_field in many2many_fields_to_apply:
        query = query.prefetch_related(
            models.Prefetch(
                many2many_field.name,
                queryset=many2many_field.related_model.objects.all(),
                to_attr=f"m2m_{many2many_field.name}"
            )
        )

    enumerable_query = query[after:after + first]

    pos = 0
    edges = [
        {
            "cursor": after + pos,
            "node": inst
        } for pos, inst in enumerate(enumerable_query)
    ]

    print("EDGES: ", edges)

    if pos < first:
        end_cursor = pos
    else:
        end_cursor = after + first - 1

    page_info = {
        "hasPreviousPage": has_previous_page,
        "startCursor": after,
        "endCursor": end_cursor
    }

    total = None
    if getTotal is True:
        total = query.count()
        page_info["total"] = total
    if getHasNextPage is True:
        if total is None:
            total = query.count()
        if total > after + first:
            page_info["hasNextPage"] = True
        else:
            page_info["hasNextPage"] = False

    return {
        "edges": edges,
        "pageInfo": page_info
    }


async def django_create(info, input: ty.Dict, Model: models.Model, gen_uid: ty.Callable) -> ty.Dict:

    snake_input = recursive_camel2snake(input)
    for field in Model._meta.get_fields():
        if isinstance(field, models.fields.related.ForeignKey):
            fk_id = snake_input.pop(f"{field.name}_id")
            snake_input[field.name] = fk_id

    response = {"error": False, "message": "Create Successfull!", "node": None}
    try:
        def create(self, validated_data):
            instance = Model.objects.create(**validated_data)
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


async def django_update(info, Model: models.Model, id: str, prevUpdated: float, input: ty.Dict) -> ty.Dict:
    snake_input = recursive_camel2snake(input)
    for field in Model._meta.get_fields():
        if isinstance(field, models.fields.related.ForeignKey):
            fk_id = snake_input.pop(f"{field.name}_id")
            snake_input[field.name] = fk_id

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
                    continue
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
