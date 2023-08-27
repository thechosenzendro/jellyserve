class RouteAlreadyDefinedError(Exception):
    pass


class UnknownRouteMethodError(Exception):
    pass


class MatcherAlreadyDefinedError(Exception):
    pass


class MessageAlreadyDefinedError(Exception):
    pass


class MiddlewareAlreadyDefinedError(Exception):
    pass

class ModelAlreadyDefinedError(Exception):
    pass

class MatcherNotFoundError(Exception):
    pass
