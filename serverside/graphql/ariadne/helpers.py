import typing as ty
from pathlib import Path
import os


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


def merge_schemas(schema_paths: ty.List[str]) -> str:
    """ This function will automatically join schemas that have been split """
    all_schema_lines = []
    all_query_lines = []
    all_mutation_lines = []
    for path in schema_paths:
        schema_lines = []
        query_lines = []
        mutation_lines = []
        assert path.endswith(".graphql"), f"schema_merger() error: <{path}> must be a .graphql file."
        assert os.path.exists(path), f"schema_merger() error: path <{path}> does not exist."
        with open(path, "r") as f:
            query_block = False
            mutation_block = False
            for line_idx, line in enumerate(f.read().split("\n")):
                if line.strip() == "type Query {":
                    query_block = True
                    continue
                elif line.strip() == "type Mutation {":
                    mutation_block = True
                    continue
                if query_block is True:
                    if line.strip() == "}":
                        query_block = False
                        continue
                    query_lines.append(line)
                elif mutation_block is True:
                    if line.strip() == "}":
                        mutation_block = False
                        continue
                    mutation_lines.append(line)
                else:
                    schema_lines.append(line)
        all_schema_lines.extend(schema_lines)
        all_query_lines.extend(query_lines)
        all_mutation_lines.extend(mutation_lines)

    schema = "\n" + "\n".join([i for i in all_schema_lines]) + \
        "\ntype Query {\n" + \
        "\n".join([j for j in all_query_lines]) + \
        "\n}" + \
        "\n\ntype Mutation {\n" + \
        "\n".join([k for k in all_mutation_lines]) + \
        "\n}\n"

    return schema
