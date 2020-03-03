import typing as ty


def get_apps(app_list: ty.List[str], prefix: str = "apps") -> ty.List:
    apps = []
    for app in app_list:
        if app.startswith(f"{prefix}."):
            apps.append(app.split(".")[-1])
    return apps
