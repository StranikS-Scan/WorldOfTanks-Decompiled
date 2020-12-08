# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/ny_toy.py
import BigWorld
from NewYearToyObject import NewYearToyObject

class NewYearToy(object):

    def __init__(self, matrix, entityProps, spaceID=None):
        if spaceID is None:
            spaceID = BigWorld.player().spaceID
        self.__toyEntityID = NewYearToyObject.createEntity(spaceID, matrix, entityProps)
        return

    @property
    def entityID(self):
        return self.__toyEntityID

    def destroy(self):
        if self.__toyEntityID is None:
            return True
        else:
            entity = BigWorld.entity(self.__toyEntityID)
            if entity is None:
                return False
            entity.destroyOutlineEntity()
            del entity
            BigWorld.destroyEntity(self.__toyEntityID)
            self.__toyEntityID = None
            return True
