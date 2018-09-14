# Embedded file name: scripts/client/tutorial/data/has_id.py


class IHasID(object):

    def getID(self):
        raise NotImplementedError

    def setID(self, entityID):
        raise NotImplementedError

    def clear(self):
        pass


class IHasTargetID(object):

    def getTargetID(self):
        raise NotImplementedError

    def setTargetID(self, targetID):
        raise NotImplementedError


class HasID(IHasID):

    def __init__(self, entityID = None, entityType = 0, **kwargs):
        super(HasID, self).__init__(**kwargs)
        self._id = entityID
        self._type = entityType

    def getID(self):
        return self._id

    def getType(self):
        return self._type

    def setID(self, entityID):
        self._id = entityID


class HasTargetID(IHasTargetID):

    def __init__(self, targetID, **kwargs):
        super(IHasTargetID, self).__init__(**kwargs)
        self._targetID = targetID

    def getTargetID(self):
        return self._targetID

    def setTargetID(self, targetID):
        self._targetID = targetID


class HasIDAndTarget(HasID, HasTargetID):

    def __init__(self, entityID = None, targetID = None, entityType = 0):
        super(HasIDAndTarget, self).__init__(entityID=entityID, targetID=targetID, entityType=entityType)
        self._targetID = targetID
