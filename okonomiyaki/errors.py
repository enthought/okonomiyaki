class OkonomiyakiError(Exception):
    pass


class InvalidPackageFormat(OkonomiyakiError):
    pass


class InvalidEggFormat(InvalidPackageFormat):
    pass


class InvalidEggName(InvalidEggFormat):
    def __init__(self, egg_name):
        msg = "Invalid egg name '{0}'".format(egg_name)
        super(InvalidEggName, self).__init__(msg)


class InvalidMetadata(InvalidEggFormat):
    def __init__(self, message, attribute, *a, **kw):
        self.message = message
        self.attribute = attribute
        super(InvalidMetadata, self).__init__(message, attribute, *a, **kw)

    def __str__(self):
        return self.message


class InvalidDependencyString(InvalidEggFormat):
    def __init__(self, dependency_string):
        msg = "Invalid dependency string {0!r}".format(dependency_string)
        super(InvalidDependencyString, self).__init__(msg)
