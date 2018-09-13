# Embedded file name: scripts/client/tutorial/data/__init__.py
from abc import ABCMeta, abstractmethod

class IHasID(object):
    __meta__ = ABCMeta

    @abstractmethod
    def getID(self):
        pass

    @abstractmethod
    def setID(self, entityID):
        pass

    def clear(self):
        pass


class IHasTargetID(object):
    __meta__ = ABCMeta

    @abstractmethod
    def getTargetID(self):
        pass

    @abstractmethod
    def setTargetID(self, targetID):
        pass


class HasID(IHasID):

    def __init__(self, entityID = None, **kwargs):
        super(HasID, self).__init__(**kwargs)
        self._id = entityID

    def getID(self):
        return self._id

    def setID(self, entityID):
        self._id = entityID


class HasTargetID(IHasTargetID):

    def __init__(self, targetID = None, **kwargs):
        super(IHasTargetID, self).__init__(**kwargs)
        self._targetID = targetID

    def getTargetID(self):
        return self._targetID

    def setTargetID(self, targetID):
        self._targetID = targetID


class HasIDAndTarget(HasID, HasTargetID):

    def __init__(self, entityID = None, targetID = None):
        super(HasIDAndTarget, self).__init__(entityID=entityID, targetID=targetID)
        self._targetID = targetID
