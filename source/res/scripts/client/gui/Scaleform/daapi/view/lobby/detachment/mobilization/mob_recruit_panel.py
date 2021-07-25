# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/detachment/mobilization/mob_recruit_panel.py
from functools import partial
from Event import Event
from gui import SystemMessages
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.MobilizationCrewMeta import MobilizationCrewMeta
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.SystemMessages import SM_TYPE
from gui.impl.auxiliary.detachmnet_convert_helper import isBarracksNotEmpty
from gui.impl.auxiliary.vehicle_helper import getBestRecruitsForVehicle
from gui.shared import EVENT_BUS_SCOPE
from gui.shared import events
from helpers import dependency
from items.components.detachment_constants import DetachmentConvertationPropertiesMasks
from skeletons.gui.shared import IItemsCache
from uilogging.detachment.constants import GROUP
from uilogging.detachment.loggers import DetachmentLogger, g_detachmentFlowLogger

class MobilizationRecruitPanel(MobilizationCrewMeta):
    itemsCache = dependency.descriptor(IItemsCache)
    uiLogger = DetachmentLogger(GROUP.MOBILIZE_CREW)

    def __init__(self):
        super(MobilizationRecruitPanel, self).__init__(eventNameSuffix='_mobilization')
        self.__vehicle = None
        self.__recruitsInvIDsWithSlots = []
        self.onUpdate = Event()
        self.onPerformConvert = Event()
        return

    @property
    def vehicleRecruitsWithSlots(self):
        return [ (slotID, self.itemsCache.items.getTankman(invID) if invID else None) for slotID, invID in self.__recruitsInvIDsWithSlots ]

    @property
    def vehicleRecruits(self):
        return [ recruit for _, recruit in sorted(self.vehicleRecruitsWithSlots, key=lambda (slotID, _): slotID) ]

    @property
    def vehicle(self):
        vehicle = self.__vehicle
        return self.itemsCache.items.getVehicle(vehicle.invID) if vehicle is not None and vehicle.isInInventory else vehicle

    def selectVehicle(self, vehicle):
        self.__vehicle = vehicle
        self.__recruitsInvIDsWithSlots = [ [slotID, recruit.invID if recruit else None] for slotID, recruit in vehicle.crew ]
        self.updateRecruitPanel()
        return

    def updateRecruitPanel(self):
        vehicle = self.vehicle
        self.as_setVisibleS(vehicle is not None)
        if not vehicle:
            return
        else:
            barracksNotEmpty = isBarracksNotEmpty(vehicle.nationID, [ invID for _, invID in self.__recruitsInvIDsWithSlots if invID ], itemsCache=self.itemsCache)
            recruitsWithSlots = self.vehicleRecruitsWithSlots
            validation, validationMask = self._validateCrewConvertion(vehicle, recruitsWithSlots, barracksNotEmpty)
            roles = self._getRoleData(vehicle, recruitsWithSlots)
            showLeaderWarning = bool(validationMask & DetachmentConvertationPropertiesMasks.PRESET)
            tankmenData = self._getRecruitsData(vehicle, recruitsWithSlots, showLeaderWarning, not barracksNotEmpty, desiredVehicleCD=vehicle.intCD)
            self.as_tankmenResponseS({'roles': roles,
             'tankmen': tankmenData,
             'autoRecruit': not barracksNotEmpty,
             'recruitFilters': self._getFilterData()})
            self._updateDogData(vehicle)
            self.onUpdate(validation, validationMask)
            return

    def setBestCrew(self, native):
        bestRecruits = getBestRecruitsForVehicle(self.vehicle, native=native)
        for slotID, invID in enumerate(bestRecruits):
            self.__replaceRecruit(slotID, invID)

        self.updateRecruitPanel()

    def equipTankman(self, tmanInvID, slotID):
        vehicle = self.vehicle
        if not vehicle:
            return
        slotID = int(slotID)
        tmanInvID = int(tmanInvID)
        if vehicle.isCrewLocked:
            SystemMessages.pushI18nMessage('#system_messages:equip_tankman/FORBIDDEN', type=SM_TYPE.Error)
            return
        result = self.__equipTankman(vehicle, slotID, tmanInvID)
        if not result:
            requiredRole = vehicle.descriptor.type.crewRoles[slotID][0]
            g_detachmentFlowLogger.flow(self.uiLogger.group, GROUP.RECRUIT_ROLE_CHANGE_DIALOG)
            self.openChangeRoleWindow(tmanInvID, requiredRole, vehicle, mobilization=True, callback=partial(self.__onRoleChanged, vehicle, slotID, tmanInvID))

    def replaceRecruit(self, recruit):
        vehicle = self.vehicle
        if not vehicle:
            return
        crewRoles = vehicle.descriptor.type.crewRoles
        for slotID, _ in vehicle.crew:
            if recruit.role in crewRoles[slotID]:
                self.__replaceRecruit(slotID, recruit.invID)
                self.updateRecruitPanel()
                return

    def openChangeRoleWindow(self, tmanInvID, requiredRole=None, vehicle=None, mobilization=False, callback=None):
        super(MobilizationRecruitPanel, self).openChangeRoleWindow(tmanInvID, requiredRole=requiredRole, vehicle=self.vehicle, mobilization=True, callback=callback)

    def onUnloadRecruits(self, *args):
        self.__recruitsInvIDsWithSlots = [ [slotID, None] for slotID, _ in self.vehicleRecruitsWithSlots ]
        self.updateRecruitPanel()
        return

    def onUnloadRecruit(self, event):
        unloadInvID = event.ctx['recruitID']
        for slotID, invID in self.__recruitsInvIDsWithSlots:
            if invID == unloadInvID:
                self.__replaceRecruit(slotID, None)
                break

        self.updateRecruitPanel()
        return

    def onSetBestCrew(self, event):
        isNative = event.ctx['isNative']
        self.setBestCrew(isNative)

    def onReturnCrew(self, *args):
        self.__recruitsInvIDsWithSlots = [ [slotID, None] for slotID, _ in self.vehicleRecruitsWithSlots ]
        for slotID, invID in enumerate(self.vehicle.lastCrew):
            recruit = self.itemsCache.items.getTankman(invID)
            if recruit is None:
                continue
            requiredRole = self.vehicle.descriptor.type.crewRoles[slotID][0]
            if requiredRole != recruit.role:
                continue
            lastRecruitVehicle = self.itemsCache.items.getVehicle(recruit.vehicleInvID)
            if lastRecruitVehicle:
                if lastRecruitVehicle.isLocked:
                    continue
            self.__replaceRecruit(slotID, invID)

        self.updateRecruitPanel()
        return

    def onConvertRecruits(self, event):
        self.onPerformConvert()

    def onOpenChangeRole(self, event):
        vehicle = self.vehicle
        recruitID = event.ctx['recruitID']
        ctx = {'tankmanID': recruitID,
         'currentVehicleCD': vehicle.descriptor.type.compactDescr,
         'mobilization': True}
        self.fireEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.ROLE_CHANGE, VIEW_ALIAS.ROLE_CHANGE), ctx=ctx), scope=EVENT_BUS_SCOPE.LOBBY)

    def onRetrainRecruits(self, *args):
        ctx = {'vehicle': self.vehicle,
         'crew': self.vehicleRecruitsWithSlots,
         'callback': self.updateRecruitPanel}
        self.fireEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.RETRAIN_CREW), ctx=ctx), EVENT_BUS_SCOPE.LOBBY)

    def __onRoleChanged(self, vehicle, slotID, tmanInvID, result):
        if not result.success:
            return
        self.__equipTankman(vehicle, slotID, tmanInvID)

    def __equipTankman(self, vehicle, slotID, recruitInvID):
        recruitInvID = int(recruitInvID)
        recruit = self.itemsCache.items.getTankman(recruitInvID)
        requiredRole = vehicle.descriptor.type.crewRoles[slotID][0]
        if requiredRole != recruit.role:
            return False
        self.__replaceRecruit(slotID, recruitInvID)
        self.updateRecruitPanel()
        return True

    def __replaceRecruit(self, slotIDToReplace, recruitInvID):
        for index, (slotID, _) in enumerate(self.__recruitsInvIDsWithSlots):
            if slotIDToReplace == slotID:
                self.__recruitsInvIDsWithSlots[index] = [slotID, recruitInvID]
                break
