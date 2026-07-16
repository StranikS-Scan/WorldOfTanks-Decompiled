# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/points_of_interest/mixins.py
import typing
import CGF
from points_of_interest.components import PoiStateComponent, PoiStateUIListenerComponent
from points_of_interest.managers import PoiStateCreateSystem
from shared_utils import first
from gui.battle_control import avatar_getter

class PointsOfInterestListener(object):

    def __init__(self):
        self.__listenerGameObject = None
        return

    def onPoiAdded(self, poiState):
        pass

    def onPoiRemoved(self, poiState):
        pass

    def onProcessPoi(self, poiState):
        pass

    def onPoiEntered(self, poiID):
        pass

    def onPoiLeft(self, poiID):
        pass

    @property
    def _poiStateSystem(self):
        spaceID = avatar_getter.getSpaceID()
        return CGF.getSystem(spaceID, PoiStateCreateSystem) if spaceID is not None else None

    @property
    def _poiStateQuery(self):
        system = self._poiStateSystem
        return system.reaction(system.StateIterate) if system is not None else []

    @property
    def _poiVehicleState(self):
        system = self._poiStateSystem
        return first(system.reaction(system.VehicleStateIterate)) if system is not None else None

    def _registerPoiListener(self, go=None):
        spaceID = avatar_getter.getSpaceID()
        if spaceID is None:
            return
        else:
            q = CGF.CommandQueue(spaceID)
            if go is None:
                p = q.createGameObject(self.__class__.__name__)
                q.activateGameObject(p)
                q.createComponent(p, PoiStateUIListenerComponent, self)
                self.__listenerGameObject = p
            else:
                q.createComponent(self.__listenerGameObject, PoiStateUIListenerComponent, self)
            q.submit()
            return

    def _unregisterPoiListener(self, go=None):
        spaceID = avatar_getter.getSpaceID()
        if spaceID is None:
            self.__listenerGameObject = None
            return
        else:
            q = CGF.CommandQueue(spaceID)
            if go is not None:
                q.removeComponent(go, PoiStateUIListenerComponent)
            elif self.__listenerGameObject is not None:
                if self.__listenerGameObject.valid:
                    q.removeGameObject(self.__listenerGameObject)
                self.__listenerGameObject = None
            q.submit()
            return
