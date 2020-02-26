from ariadne import InterfaceType


relay_node = InterfaceType("Node")


@relay_node.type_resolver
def resolve_relay_node_type(obj, *_):
    return type(obj).__name__
