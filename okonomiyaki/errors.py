class OkonomiyakiError(Exception):
    pass


class InvalidPackageFormat(OkonomiyakiError):
    pass


class UnsupportedMetadata(InvalidPackageFormat):
    pass


class InvalidEggName(InvalidPackageFormat):
    def __init__(self, egg_name):
        msg = "Invalid egg name '{0}'".format(egg_name)
        super(InvalidEggName, self).__init__(msg)


class InvalidMetadata(InvalidPackageFormat):
    def __init__(self, message, *a, **kw):
        self.message = message
        super(InvalidMetadata, self).__init__(message, *a, **kw)

    def __str__(self):
        return self.message


class InvalidRequirementString(InvalidPackageFormat):
    def __init__(self, dependency_string):
        msg = "Invalid requirement string {0!r}".format(dependency_string)
        super(InvalidRequirementString, self).__init__(msg)
