# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/goodies/GoodieResources.py


class GoodieResource(object):

    def __init__(self, value):
        self._value = value

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self._value == other._value

    def __hash__(self):
        return hash(self._value)

    def __repr__(self):
        return '<{} value={}>'.format(self.__class__.__name__, self._value)

    @property
    def value(self):
        return self._value


class Gold(GoodieResource):

    def __init__(self, value):
        super(Gold, self).__init__(value)


class Credits(GoodieResource):

    def __init__(self, value):
        super(Credits, self).__init__(value)


class Experience(GoodieResource):

    def __init__(self, value):
        super(Experience, self).__init__(value)


class CrewExperience(GoodieResource):

    def __init__(self, value):
        super(CrewExperience, self).__init__(value)


class FreeExperience(GoodieResource):

    def __init__(self, value):
        super(FreeExperience, self).__init__(value)


class ResourceDescription(object):
    __slots__ = ['resource', 'value']

    def __init__(self, resource, value):
        self.resource = resource
        self.value = value


class FrontlineExperience(GoodieResource):

    def __init__(self, value):
        super(FrontlineExperience, self).__init__(value)
