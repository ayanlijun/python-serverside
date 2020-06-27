
def django_get(Model: django.db.models.Model, id: str) -> django.db.models.Model:
    try:
        return Model.objects.get(id=id)
    except Model.DoesNotExist:
        return None


def django_create(
    Model: django.db.models.Model,
    id: str,
    input: ty.Dict,
    handlers: ty.Dict
):
    response = {"error": False, "message": None, "node": None}
    try:
        inst = Model(id=id)
        for ik, iv in input.items():
            snake_ik = inflection.underscore(ik)
            if snake_ik in handlers:
                inst = handlers[ik](iv)
            else:
                setattr(inst, snake_ik, iv)
        inst.save()
        return {**response, "node": inst}
    except Model.DoesNotExist:
        return {**response, "error": True, "message": f"An `{Model.__name__}` does not exist with the id `{id}`"}
    except Exception as err:
        return {**response, "error": True, "message": f"Updating {Model.__name__} with id<{id}> failed because: {err}"}


def django_update(
    Model: django.db.models.Model,
    id: str,
    prev_updated: float,
    input: ty.Dict,
    handlers: ty.Dict
):
    response = {"error": False, "message": None, "node": None}
    try:
        inst = Model.objects.get(id=id)
        assert prev_updated == inst.updated.timestamp()
        for ik, iv in input.items():
            snake_ik = inflection.underscore(ik)
            if snake_ik in handlers:
                inst = handlers[ik](iv)
            else:
                setattr(inst, snake_ik, iv)
        inst.save()
        return {**response, "node": inst}
    except Model.DoesNotExist:
        return {**response, "error": True, "message": f"An `{Model.__name__}` does not exist with the id `{id}`"}
    except Exception as err:
        return {**response, "error": True, "message": f"Updating {Model.__name__} with id<{id}> failed because: {err}"}


def django_delete(Model: django.db.models.Model, id: str, prevUpdated: float):
    response = {"error": False, "message": None}
    try:
        emotion_inst = Model.objects.get(id=id)
        assert prevUpdated == emotion_inst.updated.timestamp()
        emotion_inst.delete()
        return response
    except Model.DoesNotExist:
        return {**response, "error": True, "message": f"An {Model.__name__} does not exist with the id `{id}`"}
    except Exception as err:
        return {**response, "error": True, "message": f"Deleting {Model.__name__} with id<{id}> failed because: {err}"}
    return response


class DjangoQuery:

    SORT_ASC = "asc"
    SORT_DESC = "desc"
    VALID_SORT_DIRECTIONS = [SORT_DESC, SORT_ASC]

    def __init__(self, Model: django.db.models.Model, kwargs: ty.Dict):
        self.first = kwargs.pop("first", settings.PAGINATION_SIZE)
        self.after = kwargs.pop("after", None)
        self.before = kwargs.pop("before", None)
        self.sort_by = kwargs.pop("sortBy", None)
        self.sort_direction = kwargs.pop("sortDirection", "desc")
        assert self.sort_direction in DjangoQuery.VALID_SORT_DIRECTIONS
        self.filters = kwargs

        self.get_total = False
        self.get_has_next_page = False

        self._model = Model
        self.objs = self._model.objects

        self._query_fields = None

    def apply_filters(self):
        print("Apply Filters...")
        if self.filters:
            for qfk, qfv in self.filters.items():
                self.objs = self.objs.filter(**{inflection.underscore(qfk): qfv})
        else:
            self.objs = self.objs.all()
        return self

    def get_query_fields(self, info, field: str):
        print("Get Query Fields...")
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
                                self.get_total = True
                            elif l3v.name.value == "hasNextPage":
                                self.get_has_next_page = True
                            elif l3v.name.value == "hasPreviousPage":
                                pass
                            elif l3v.name.value == "startCursor":
                                pass
                            elif l3v.name.value == "endCursor":
                                pass
        camel_query_fields = [i for i in camel_query_fields if not i.startswith("__")]
        snake_query_fields = [inflection.underscore(field) for field in camel_query_fields]

        regular_fields = []
        foreignkey_fields = []
        self.foreignkey_fields_to_apply = []
        many2many_fields = []
        self.many2many_fields_to_apply = []
        many2one_fields = []
        self.many2one_fields_to_apply = []
        for field in self._model._meta.get_fields():
            if isinstance(field, django.db.models.fields.related.ForeignKey):
                foreignkey_fields.append(field)
                if field.name in snake_query_fields:
                    self.foreignkey_fields_to_apply.append(field)
            elif isinstance(field, django.db.models.fields.related.ManyToManyField):
                many2many_fields.append(field)
                if field.name in snake_query_fields:
                    self.many2many_fields_to_apply.append(field)
            elif isinstance(field, django.db.models.fields.reverse_related.ManyToOneRel):
                many2one_fields.append(field)
                if field.name in snake_query_fields:
                    self.many2one_fields_to_apply.append(field)
            elif isinstance(field, django.db.models.fields.reverse_related.ManyToManyRel):
                pass
            else:
                regular_fields.append(field.name)

        snake_query_fields = [i for i in snake_query_fields if i in regular_fields]
        self._query_fields = regular_fields + [i.name for i in self.foreignkey_fields_to_apply]
        return self

    def onlyfy(self):
        settings.LOGGER.debug("Onlyfy...")
        if self._query_fields is None:
            raise Exception("You can't call `onlyfy()` without first running `get_query_fields()`")
        if isinstance(self.objs, django.db.models.manager.Manager):
            raise Exception("You can't call `onlyfy()` without first generating a `QuerySet`")
        self.objs = self.objs.only(*self._query_fields)
        return self

    def prefetch(self, m2m_prefix: str = "m2m_", m2o_prefix: str = "m2o_"):
        settings.LOGGER.debug("Prefetch...")
        if self._query_fields is None:
            raise Exception("You can't call `prefetch()` without first running `get_query_fields()`")
        if isinstance(self.objs, django.db.models.manager.Manager):
            raise Exception("You can't call `prefetch()` without first generating a `QuerySet`")
        for foreignkey_field in self.foreignkey_fields_to_apply:
            self.objs = self.objs.select_related(foreignkey_field.name)
        for many2one_field in self.many2one_fields_to_apply:
            self.objs = self.objs.prefetch_related(
                django.db.models.Prefetch(
                    many2one_field.name,
                    queryset=many2one_field.related_model.objects.all(),
                    to_attr=f"{m2o_prefix}{many2one_field.name}"
                )
            )
        for many2many_field in self.many2many_fields_to_apply:
            self.objs = self.objs.prefetch_related(
                django.db.models.Prefetch(
                    many2many_field.name,
                    queryset=many2many_field.related_model.objects.all(),
                    to_attr=f"{m2m_prefix}{many2many_field.name}"
                )
            )
        return self

    def fetch(self):
        settings.LOGGER.debug("Fetch...")
        has_previous_page = False
        if self.after is not None and self.before is not None:
            raise Exception("You can't query with both `before` and `after`")
        elif self.after is None and self.before is None:
            self.after = 0
        elif self.after is not None and self.before is None:
            if self.after != 0:
                self.after = self.after + 1  # So as to start from the idx AFTER the integer given
                has_previous_page = True
        elif self.after is None and self.before is not None:
            self.after = self.before - self.first
        after = max(self.after, 0)

        # Sort by and Sort direction
        if self.sort_by is not None:
            if self.sort_direction == DjangoQuery.SORT_DESC:
                self.objs = self.objs.order_by(f"-{self.sort_by}")
            else:
                self.objs = self.objs.order_by(self.sort_by)

        self.non_paged_objs = self.objs
        self.objs = self.objs[self.after:self.after + self.first]
        pos = 0
        edges = [
            {
                "cursor": after + pos,
                "node": inst
            } for pos, inst in enumerate(self.objs)
        ]
        if pos < self.first:
            end_cursor = pos
        else:
            end_cursor = after + self.first - 1
        page_info = {
            "hasPreviousPage": has_previous_page,
            "startCursor": after,
            "endCursor": end_cursor
        }
        total = None
        if self.get_total is True:
            total = self.non_paged_objs.count()
            page_info["total"] = total
        if self.get_has_next_page is True:
            if total > after + self.first:
                page_info["hasNextPage"] = True
            else:
                page_info["hasNextPage"] = False
        return {
            "edges": edges,
            "pageInfo": page_info
        }

    def apply_all(self, info: object, field: str):
        return self.get_query_fields(info, field=field) \
            .apply_filters() \
            .onlyfy() \
            .prefetch() \
            .fetch()


__all__ = [
    "DjangoQuery",
    "django_get",
    "django_create",
    "django_update",
    "django_delete"
]
