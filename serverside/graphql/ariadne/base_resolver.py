import ariadne


class BaseResolver:

    @classmethod
    def export_resolvers(cls):
        return[getattr(cls, var) for var in vars(cls) if isinstance(getattr(cls, var), ariadne.objects.ObjectType)]
