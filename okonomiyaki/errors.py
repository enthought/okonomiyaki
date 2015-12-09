class OkonomiyakiError(Exception):
    pass


class InvalidPackageFormat(OkonomiyakiError):
    pass


class UnsupportedMetadata(InvalidPackageFormat):
    def __init__(self, metadata_version, *a, **kw):
        self.metadata_version = metadata_version
        super(UnsupportedMetadata, self).__init__(*a, **kw)

    def __str__(self):
        if len(self.args) >= 1:
            return self.args[0]
        else:
            return "Unsupported metadata_version: {0!r}".format(
                str(self.metadata_version))


class InvalidEggName(InvalidPackageFormat):
    def __init__(self, egg_name):
        self.egg_name = egg_name
        msg = "Invalid egg name '{0}'".format(egg_name)
        super(InvalidEggName, self).__init__(msg)


class InvalidMetadata(InvalidPackageFormat):
    def __init__(self, message, *a, **kw):
        self.message = message
        super(InvalidMetadata, self).__init__(message, *a, **kw)

    def __str__(self):
        return self.message


class _undefined(object):
    def __repr__(self):
        return '<undefined>'


class InvalidMetadataField(InvalidMetadata):

    undefined = _undefined()

    def __init__(self, name, value, *a, **kw):
        self.name = name
        self.value = value
        message = 'Metadata field is invalid ({0} = {1!r})'.format(
            name, value)
        super(InvalidMetadataField, self).__init__(message, *a, **kw)


class MissingMetadata(InvalidMetadata):
    pass


class InvalidRequirementString(InvalidPackageFormat):
    def __init__(self, requirement_string):
        self.requirement_string = requirement_string
        msg = "Invalid requirement string {0!r}".format(requirement_string)
        super(InvalidRequirementString, self).__init__(msg)
