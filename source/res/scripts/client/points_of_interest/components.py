# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/points_of_interest/components.py
import enum
import typing
import BigWorld
import CGF
if typing.TYPE_CHECKING:
    from points_of_interest_shared import PoiType
    from helpers.fixed_dict import StatusWithTimeInterval
    from points_of_interest.mixins import PointsOfInterestListener

@enum.unique
class PoiStateUpdateMask(enum.IntEnum):
    NONE = 0
    PROGRESS = 1
    INVADER = 2
    STATUS = 4
    ALL = PROGRESS | INVADER | STATUS


class PoiStateComponent(object):
    __slots__ = ('id', 'type', '_progress', '_invader', '_status', '_updatedFields')

    def __init__(self, poiID, poiType, progress, invader, status):
        self.id = poiID
        self.type = poiType
        self._progress = progress
        self._invader = invader
        self._status = status
        self._updatedFields = PoiStateUpdateMask.ALL

    @property
    def progress(self):
        return self._progress

    @progress.setter
    def progress(self, progress):
        self._progress = progress
        self._updatedFields |= PoiStateUpdateMask.PROGRESS

    @property
    def invader(self):
        return self._invader

    @invader.setter
    def invader(self, invader):
        self._invader = invader
        self._updatedFields |= PoiStateUpdateMask.INVADER

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status):
        self._status = status
        self._updatedFields |= PoiStateUpdateMask.STATUS

    @property
    def updatedFields(self):
        return self._updatedFields

    def resetUpdatedFields(self):
        self._updatedFields = PoiStateUpdateMask.NONE


class PoiStateUIListenerComponent(object):
    __slots__ = ('listener',)

    def __init__(self, listener):
        self.listener = listener


class PoiCaptureBlockerStateComponent(object):
    __slots__ = ('id', 'blockReasons', 'poiState')

    def __init__(self, poiID, blockReasons):
        self.id = poiID
        self.blockReasons = blockReasons
        poi = BigWorld.entities.get(poiID)
        self.poiState = CGF.ComponentLink(poi.entityGameObject, PoiStateComponent) if poi is not None else None
        return


class PoiVehicleStateComponent(object):
    __slots__ = ('id',)

    def __init__(self, poiID):
        self.id = poiID
