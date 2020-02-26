def extract_actions_from_query(query: str):
    assert isinstance(query, str)
    query = query.strip()

    if query.startswith("query IntrospectionQuery"):
        return ["IntrospectionQuery"]

    if not query.startswith(("query {", "mutation {")):  # Apollo Variable Reference
        query = "{".join(i for i in query.split("{")[1:])
        query = "}".join(i for i in query.split("}")[:-1])
    # variables = body.get("variables")

    query = query.replace("mutation ", "")
    query = query.replace("query ", "")

    actions = []
    curly_cnt = 0
    roundy_cnt = 0
    action_string = ""

    for idx, char in enumerate(query[2:]):
        if char == "{":
            curly_cnt += 1
        elif char == "}":
            curly_cnt -= 1
        if curly_cnt > 0:
            continue

        if char == "(":
            roundy_cnt += 1
        elif char == ")":
            roundy_cnt -= 1
        if roundy_cnt > 0:
            continue

        if char in [" ", "\n"]:
            if len(action_string) > 0:
                actions.append(action_string)
                action_string = ""
        elif char in ["{", "}", "(", ")"]:
            continue
        else:
            action_string += char

    return actions
