# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortBuildingComponent.py
from ClientFortifiedRegion import BUILDING_UPDATE_REASON
from debug_utils import LOG_DEBUG
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortSoundController import g_fortSoundController
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortTransportationViewHelper import FortTransportationViewHelper
from constants import FORT_BUILDING_TYPE
from gui.shared import events
from gui.shared import EVENT_BUS_SCOPE
from gui.Scaleform.daapi.view.meta.FortBuildingComponentMeta import FortBuildingComponentMeta
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.shared.events import FortEvent

class FortBuildingComponent(FortBuildingComponentMeta, FortTransportationViewHelper):

    def __init__(self):
        super(FortBuildingComponent, self).__init__()
        self.__isOnNextTransportingStep = False
        self._animation = None
        return

    def _populate(self):
        super(FortBuildingComponent, self)._populate()
        self.startFortListening()
        self.addListener(events.FortEvent.TRANSPORTATION_STEP, self.__onTransportingStep, scope=EVENT_BUS_SCOPE.FORT)
        self.updateData()

    def _dispose(self):
        self.removeListener(events.FortEvent.TRANSPORTATION_STEP, self.__onTransportingStep, scope=EVENT_BUS_SCOPE.FORT)
        self.stopFortListening()
        self._animation = None
        super(FortBuildingComponent, self)._dispose()
        return

    def updateData(self, animations = None):
        self.__makeData(animations)

    def onWindowClose(self):
        self.destroy()

    def onTransportingRequest(self, exportFrom, importTo):
        self.fireEvent(events.LoadViewEvent(FortEvent.REQUEST_TRANSPORTATION, ctx={'fromId': exportFrom,
         'toId': importTo}), EVENT_BUS_SCOPE.FORT)

    def requestBuildingProcess(self, direction, position):
        self.fireEvent(events.LoadViewEvent(FORTIFICATION_ALIASES.FORT_BUILDING_PROCESS_WINDOW_ALIAS, ctx={'buildingDirection': direction,
         'buildingPosition': position}), EVENT_BUS_SCOPE.LOBBY)

    def upgradeVisitedBuilding(self, uid):
        if not self._isAvailableBlinking():
            return
        buildingID = self.getBuildingIDbyUID(uid)
        limits = self.fortCtrl.getLimits()
        isLevelUp, _ = limits.canUpgrade(buildingID)
        if isLevelUp:
            self.fortCtrl.addUpgradeVisitedBuildings(buildingID)

    def requestBuildingToolTipData(self, uid, type):
        buildingDescr = self.fortCtrl.getFort().getBuilding(self.getBuildingIDbyUID(uid))
        self.as_setBuildingToolTipDataS(uid, type, self.getCommonBuildTooltipData(buildingDescr))

    def onUpdated(self, isFullUpdate):
        if self._animation is not None or isFullUpdate:
            self.updateData(self._animation)
            self._animation = None
        return

    def onStateChanged(self, state):
        self.updateData(self._animation)

    def onBuildingChanged(self, buildingID, reason, ctx = None):
        animations = {}
        if reason == BUILDING_UPDATE_REASON.COMPLETED:
            uid = self.getBuildingUIDbyID(buildingID)
            g_fortSoundController.playCompletedBuilding(uid)
        if reason in self.BUILDING_ANIMATIONS:
            dir = ctx.get('dir')
            pos = ctx.get('pos')
            animations[dir, pos] = self.BUILDING_ANIMATIONS[reason]
        if reason == BUILDING_UPDATE_REASON.UPGRADED:
            self._animation = animations
        else:
            self.updateData(animations)

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

    def onDirectionOpened(self, dir):
        self.updateData()

    def onDirectionClosed(self, dir):
        self.updateData()

    def onOrderChanged(self, orderTypeID, reason):
        self.updateData()

    def onShutdownDowngrade(self):
        self.updateData()

    def onDefenceHourStateChanged(self):
        self.updateData()

    def onDirectionLockChanged(self):
        self.updateData()

    def isOnNextTransportingStep(self):
        return self.__isOnNextTransportingStep

    def __onTransportingConfirmed(self, event):
        self.as_refreshTransportingS()

    def __onTransportingStep(self, event):
        step = event.ctx.get('step')
        self.__isOnNextTransportingStep = step == events.FortEvent.TRANSPORTATION_STEPS.NEXT_STEP
        self.updateData()

    def __makeData(self, animations = None):
        b_list = []
        baseBuildingDescr = self.fortCtrl.getFort().getBuilding(FORT_BUILDING_TYPE.MILITARY_BASE)
        animation = FORTIFICATION_ALIASES.WITHOUT_ANIMATION
        if animations is not None and (0, 0) in animations:
            animation = animations[(0, 0)]
            LOG_DEBUG('Playing building animation', 0, 0, animation)
        b_list.append(self._makeBuildingData(baseBuildingDescr, 0, 0, False, animation))
        for direction, buildings in self.fortCtrl.getFort().getBuildingsByDirections().iteritems():
            for position, building in enumerate(buildings):
                animation = FORTIFICATION_ALIASES.WITHOUT_ANIMATION
                if animations is not None and (direction, position) in animations:
                    animation = animations[direction, position]
                    LOG_DEBUG('Playing building animation', direction, position, animation)
                buildingData = self._makeBuildingData(building, direction, position, False, animation)
                b_list.append(buildingData)

        data = {'canAddBuilding': self.fortCtrl.getPermissions().canAddBuilding(),
         'buildingData': b_list}
        self.as_setDataS(data)
        return
