class OkonomiyakiError(Exception):
    pass


class InvalidEggName(OkonomiyakiError):
    def __init__(self, egg_name):
        msg = "Invalid egg name '{0}'".format(egg_name)
        super(InvalidEggName, self).__init__(msg)


class InvalidDependencyString(OkonomiyakiError):
    def __init__(self, dependency_string):
        msg = "Invalid dependency string '{0}'".format(dependency_string)
        super(InvalidDependencyString, self).__init__(msg)
