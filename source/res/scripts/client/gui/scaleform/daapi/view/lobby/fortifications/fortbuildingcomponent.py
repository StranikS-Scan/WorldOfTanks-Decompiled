# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortBuildingComponent.py
from debug_utils import LOG_DEBUG
from gui.Scaleform.daapi.view.lobby.fortifications import TRANSPORTING_CONFIRMED_EVENT
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortTransportationViewHelper import FortTransportationViewHelper
from gui.shared.SoundEffectsId import SoundEffectsId
from constants import FORT_BUILDING_TYPE
from gui.shared import events
from gui.shared import EVENT_BUS_SCOPE
from gui.Scaleform.daapi.view.meta.FortBuildingComponentMeta import FortBuildingComponentMeta
from gui.Scaleform.framework import AppRef
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES

class FortBuildingComponent(FortBuildingComponentMeta, FortTransportationViewHelper, AppRef):

    def __init__(self):
        super(FortBuildingComponent, self).__init__()
        self.__isOnNextTransportingStep = False

    def _populate(self):
        super(FortBuildingComponent, self)._populate()
        self.startFortListening()
        self.addListener(TRANSPORTING_CONFIRMED_EVENT, self.__onTransportingConfirmed, scope=EVENT_BUS_SCOPE.FORT)
        self.addListener(events.FortEvent.TRANSPORTATION_STEP, self.__onTransportingStep, scope=EVENT_BUS_SCOPE.FORT)
        self.updateData()

    def _dispose(self):
        self.removeListener(TRANSPORTING_CONFIRMED_EVENT, self.__onTransportingConfirmed, scope=EVENT_BUS_SCOPE.FORT)
        self.removeListener(events.FortEvent.TRANSPORTATION_STEP, self.__onTransportingStep, scope=EVENT_BUS_SCOPE.FORT)
        self.stopFortListening()
        super(FortBuildingComponent, self)._dispose()

    def updateData(self):
        self.__makeData()

    def onWindowClose(self):
        self.destroy()

    def onTransportingRequest(self, exportFrom, importTo):
        self.fireEvent(events.ShowViewEvent(FORTIFICATION_ALIASES.FORT_TRANSPORT_CONFIRMATION_WINDOW_EVENT, {'fromId': exportFrom,
         'toId': importTo}), EVENT_BUS_SCOPE.LOBBY)

    def requestBuildingProcess(self, direction, position):
        self.fireEvent(events.ShowViewEvent(FORTIFICATION_ALIASES.FORT_BUILDING_PROCESS_WINDOW_EVENT, ctx={'buildingDirection': direction,
         'buildingPosition': position}), EVENT_BUS_SCOPE.LOBBY)

    def upgradeVisitedBuilding(self, uid):
        if not self._isAvailableBlinking():
            return
        buildingID = self.UI_BUILDINGS_BIND.index(uid)
        limits = self.fortCtrl.getLimits()
        isLevelUp, _ = limits.canUpgrade(buildingID)
        if isLevelUp:
            self.fortCtrl.addUpgradeVisitedBuildings(buildingID)

    def __makeData(self):
        b_list = []
        baseBuildingDescr = self.fortCtrl.getFort().getBuilding(FORT_BUILDING_TYPE.MILITARY_BASE)
        b_list.append(self._makeBuildingData(baseBuildingDescr, 0, 0, False))
        for direction, buildings in self.fortCtrl.getFort().getBuildingsByDirections().iteritems():
            for position, building in enumerate(buildings):
                buildingData = self._makeBuildingData(building, direction, position, False)
                b_list.append(buildingData)

        data = {'isCommander': self._isChiefRoles(),
         'buildingData': b_list}
        self.as_setDataS(data)

    def getBuildingTooltipData(self, uid):
        buildingDescr = self.fortCtrl.getFort().getBuilding(self.UI_BUILDINGS_BIND.index(uid))
        return [uid, self.getCommonBuildTooltipData(buildingDescr)]

    def onUpdated(self):
        self.updateData()

    def onBuildingChanged(self, buildingID, reason, ctx = None):
        if reason == self.fortCtrl.getFort().BUILDING_UPDATE_REASON.COMPLETED:
            uid = self.UI_BUILDINGS_BIND[buildingID]
            if self.app.soundManager is not None:
                self.app.soundManager.playEffectSound(SoundEffectsId.getEndBuildingProcess(uid))
        return

    def onBuildingsUpdated(self, buildingsTypeIDs, cooldownPassed = False):
        if cooldownPassed:
            self.updateData()
        else:
            for buildingTypeID in buildingsTypeIDs:
                building = self.fortCtrl.getFort().getBuilding(buildingTypeID)
                self.as_setBuildingDataS(self._makeBuildingData(building, building.direction, building.position, False))
                self.updateData()

    def onUpgradeVisitedBuildingChanged(self, buildingID):
        self.updateData()

    def isOnNextTransportingStep(self):
        return self.__isOnNextTransportingStep

    def __onTransportingConfirmed(self, event):
        self.as_refreshTransportingS()

    def __onTransportingStep(self, event):
        step = event.ctx.get('step')
        self.__isOnNextTransportingStep = step == events.FortEvent.TRANSPORTATION_STEPS.FIRST_STEP
        self.__makeData()
