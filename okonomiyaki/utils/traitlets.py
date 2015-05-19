from ..bundled.traitlets import Instance, Unicode


class NoneOrUnicode(Unicode):

    default_value = None
    info_text = 'None or a unicode string'

    def validate(self, obj, value):
        if value is None:
            return None
        return super(NoneOrUnicode, self).validate(obj, value)


class NoneOrInstance(Instance):

    default_value = None
    info_text = 'None or a instance'

    def validate(self, obj, value):
        if value is None:
            return None
        return super(NoneOrInstance, self).validate(obj, value)
