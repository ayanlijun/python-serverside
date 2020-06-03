import ariadne


def objecttype(object_name: str):
    def wrapper(wrapped):
        setattr(wrapped, "OBJECT", ariadne.ObjectType(object_name))
        setattr(wrapped, "_objectname", object_name)
        return wrapped
    return wrapper


def ignore_fields_for_camel_conversion(*args):
    def wrapper(wrapped):
        for field_name in args:
            print("setting ___ ", field_name)
            setattr(wrapped, f"IGNORE_FIELDS_FOR_CAMEL_CONVERSION_{field_name}", True)
        return wrapped
    return wrapper
