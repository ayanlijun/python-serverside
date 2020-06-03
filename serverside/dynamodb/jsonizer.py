from inspect import ismethod
import traceback
import logging
import json

from pynamodb.models import Model as PynamodbModel


class BaseJsonizer:

    def __init__(self, logger: logging.Logger = None):
        self._logger = logger

    def render(self, attrs, obj):
        if obj:
            d = {}
            for attr in attrs:
                try:
                    d[attr] = self.__fetch_attribute(obj, attr)
                except KeyError as key_err:
                    if self._logger is not None:
                        self._logger.error(f"Dynamodb BaseJsonizer raised KeyError: (err{key_err}, class={self.__class__})")
                except Exception as err:
                    if self._logger is not None:
                        err_msg = {
                            "err": str(err),
                            "class": str(obj.__class__),
                            "attr": attr,
                            "attrs": attrs,
                            "obj": obj,
                            "traceback": traceback.format_exc()
                        }
                        self._logger.error(f"Dynamodb BaseJsonizer Exception: {json.dumps(err_msg).decode('utf-8')}")
            return d

    def __fetch_attribute(self, obj, attr):
        print(f"TMP!!!!!! DYNAMODB SERIALIZER FETCHING ATTRIBUTE(obj={obj}, attr={attr}) ")
        attr = f"get_{attr}"  # Follow Django Serializer convention with attribute fields prefixed with `get_`
        if hasattr(self, attr):
            temp_attr = getattr(self, attr)
            if ismethod(temp_attr):
                try:
                    return temp_attr()
                except TypeError:
                    return temp_attr(obj)
            return temp_attr
        elif hasattr(obj, attr):
            temp_attr = getattr(obj, attr)
            if ismethod(temp_attr):
                return temp_attr()
            return temp_attr
        elif isinstance(obj, dict):
            return obj.get(attr, None)


class Jsonizer(BaseJsonizer):

    def __init__(self, obj, many=False, context=None, attrs_type=None):
        self.object = obj
        self.many = many
        self.context = context
        self.attrs = None

        tmpobj = obj if not self.many or not obj else obj[0]

        if isinstance(tmpobj, PynamodbModel) and not attrs_type:
            self.attrs = tmpobj.attribute_values.keys()
        elif isinstance(tmpobj, dict) and not attrs_type:
            self.attrs = tmpobj.keys()
        elif tmpobj and attrs_type:
            self.attrs = list(getattr(self, f"ATTRS_{attrs_type.upper()}"))
        elif attrs_type:
            self.attrs = attrs_type
        else:
            if self._logger is not None:
                self._logger.error(f"Dynamodb Jsonizer Attribute Type Error: (obj={obj}, many={many}, attrs_type={attrs_type}, tmpobj={tmpobj})")

    @property
    def data(self):
        return self.render()

    def render(self):
        if self.many:
            return [super(Jsonizer, self).render(self.attrs, obj) for obj in self.object] if self.object is not None else None
        else:
            return super(Jsonizer, self).render(self.attrs, self.object) if self.object is not None else None
