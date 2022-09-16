# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/points_of_interest/mixins.py
import typing
import CGF
from points_of_interest.components import PoiStateComponent, PoiStateUIListenerComponent, PoiVehicleStateComponent
from shared_utils import first
from gui.battle_control import avatar_getter

class PointsOfInterestListener(object):

    def __init__(self):
        self.__listenerGameObject = None
        return

    @property
    def _poiStateQuery(self):
        spaceID = avatar_getter.getSpaceID()
        return CGF.Query(spaceID, PoiStateComponent) if spaceID is not None else []

    @property
    def _poiVehicleState(self):
        spaceID = avatar_getter.getSpaceID()
        return first(CGF.Query(spaceID, PoiVehicleStateComponent)) if spaceID is not None else None

    def onPoiAdded(self, state):
        pass

    def onPoiRemoved(self, state):
        pass

    def onProcessPoi(self, state):
        pass

    def onPoiEntered(self, poiID):
        pass

    def onPoiLeft(self, poiID):
        pass

    def _registerPoiListener(self, go=None):
        spaceID = avatar_getter.getSpaceID()
        if spaceID is None:
            return
        else:
            if go is None:
                self.__listenerGameObject = go = CGF.GameObject(spaceID, self.__class__.__name__)
                go.activate()
            go.createComponent(PoiStateUIListenerComponent, self)
            return

    def _unregisterPoiListener(self, go=None):
        if go is not None:
            go.removeComponentByType(PoiStateUIListenerComponent)
        elif self.__listenerGameObject is not None:
            if self.__listenerGameObject.isValid():
                self.__listenerGameObject.destroy()
            self.__listenerGameObject = None
        return
