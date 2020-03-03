import inflection
from django.db import models


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
