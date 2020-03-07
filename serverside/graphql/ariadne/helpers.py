import typing as ty


def combine_resolvers(exported_resolvers: ty.List) -> ty.List:
    resolvers = []
    for er in exported_resolvers:
        for resolver in er():
            try:
                resolvers.extend(resolver.export_resolvers())
                resolver.auto_cruderize()
            except Exception:
                continue
    return resolvers


class AutoCrud:

    def __init__(self, count: str, get_one: str, get_many: str, create: str, update: str, delete: str):
        self.count = count
        self.get_one = get_one
        self.get_many = get_many
        self.create = create
        self.update = update
        self.delete = delete


def auto_crud(
    count: str = None,
    get_one: str = None,
    get_many: str = None,
    create: str = None,
    update: str = None,
    delete: str = None
):
    return AutoCrud(
        count=count,
        get_one=get_one,
        get_many=get_many,
        create=create,
        update=update,
        delete=delete
    )
