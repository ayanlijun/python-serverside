import rest_framework
import inflection


def camelize(obj):
    if isinstance(obj, dict):
        if isinstance(obj, rest_framework.utils.serializer_helpers.ReturnDict):
            new = {}
        else:
            new = obj.__class__()
        for k, v in obj.items():
            new[inflection.camelize(k, False)] = camelize(v)
    elif isinstance(obj, (list, set, tuple)):
        new = obj.__class__(camelize(o) for o in obj)
    else:
        return obj
    return new
