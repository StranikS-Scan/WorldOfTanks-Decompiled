# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/crewOperations/CrewOperationsPopOver.py
from CurrentVehicle import g_currentVehicle
from gui.ClientUpdateManager import g_clientUpdateManager
from account_helpers import AccountSettings
from account_helpers.AccountSettings import BEST_CREW_OPTION_USED
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.CrewOperationsPopOverMeta import CrewOperationsPopOverMeta
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.impl import backport
from gui.impl.auxiliary.vehicle_helper import validateBestCrewForVehicle, getBestRecruitsForVehicle
from gui.impl.gen import R
from gui.prb_control import prb_getters
from gui.shared import EVENT_BUS_SCOPE, events
from gui.shared.events import LoadViewEvent
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from helpers import dependency
from skeletons.gui.detachment import IDetachmentCache
from skeletons.gui.shared import IItemsCache
from shared_utils import first
from uilogging.detachment.loggers import DetachmentLogger, g_detachmentFlowLogger
from uilogging.detachment.constants import ACTION, GROUP
OPERATION_RETRAIN = 'retrain'
OPERATION_RETURN = 'returnOldCrew'
OPERATION_DROP_IN_BARRACK_OLD_CREW = 'dropInBarrackOldCrew'
OPERATION_SET_BEST_CREW = 'setBestCrew'
PREV_CREW_WARNING_MEMBERS_IN_BATTLE = 'membersInBattle'
PREV_CREW_WARNING_RETRAINED = 'membersRetrained'
PREV_CREW_WARNING_DEMOBILIZED = 'membersDemobilized'
PREV_CREW_WARNING_COMPOUND = 'universal'

class CrewOperationsPopOver(CrewOperationsPopOverMeta):
    itemsCache = dependency.descriptor(IItemsCache)
    detachmentCache = dependency.descriptor(IDetachmentCache)
    uiDetachmentLogger = DetachmentLogger(GROUP.RECRUIT_ACTIONS_CONTEXT_MENU)

    def _populate(self):
        super(CrewOperationsPopOver, self)._populate()
        g_clientUpdateManager.addCallbacks({'inventory': self.onInventoryUpdate})
        unitMgr = prb_getters.getClientUnitMgr()
        if unitMgr:
            unitMgr.onUnitLeft += self.__unitMgrOnUnitLeft
        self.__update()

    def onWindowClose(self):
        self.destroy()

    def _destroy(self):
        unitMgr = prb_getters.getClientUnitMgr()
        if unitMgr:
            unitMgr.onUnitLeft -= self.__unitMgrOnUnitLeft
        super(CrewOperationsPopOver, self)._destroy()

    def _dispose(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(CrewOperationsPopOver, self)._dispose()

    def onInventoryUpdate(self, invDiff):
        if GUI_ITEM_TYPE.TANKMAN in invDiff:
            self.__update()

    def __update(self):
        vehicle = g_currentVehicle.item
        data = {'operationsArray': [self.__getBestCrewOperationData(vehicle),
                             self.__getReturnOperationData(vehicle),
                             self.__getRetrainOperationData(vehicle),
                             self.__getDropInBarrackOldCrewOperationData()]}
        self.as_updateS(data)

    def __getBestCrewOperationData(self, vehicle):
        hint = ''
        if not AccountSettings.getSettings(BEST_CREW_OPTION_USED):
            hint = backport.text(R.strings.menu.counter.newCounter())
        crew = [ (recruit.invID if recruit is not None else None) for _, recruit in vehicle.crew ]
        isCrewFullyEquipped = all((recruit is not None for recruit in getBestRecruitsForVehicle(vehicle)))
        if validateBestCrewForVehicle(vehicle, crew):
            if self.__getAvailableRecruits(vehicle.nationID) == 0 and not isCrewFullyEquipped:
                return self.__getInitCrewOperationObject(OPERATION_SET_BEST_CREW, 'noCrew', hintValue=hint)
            return self.__getInitCrewOperationObject(OPERATION_SET_BEST_CREW, 'alreadySet', hintValue=hint)
        else:
            return self.__getInitCrewOperationObject(OPERATION_SET_BEST_CREW, hintValue=hint)

    def __getReturnOperationData(self, vehicle):
        lastCrewIDs = vehicle.lastCrew
        currentCrew = [ (recruit.invID if recruit is not None else None) for _, recruit in vehicle.crew ]
        if lastCrewIDs is None:
            return self.__getInitCrewOperationObject(OPERATION_RETURN, 'noPrevious')
        elif set(lastCrewIDs) == set(currentCrew):
            return self.__getInitCrewOperationObject(OPERATION_RETURN, 'alreadyOnPlaces')
        else:
            lastRecruits = [ self.itemsCache.items.getTankman(recruitInvID) for recruitInvID in lastCrewIDs ]
            if all((recruit is None or recruit.invID in currentCrew for recruit in lastRecruits)):
                return self.__getInitCrewOperationObject(OPERATION_RETURN, 'allDemobilized')
            reason = None
            isOpAvailable = False
            crewRoles = [ first(roles) for roles in vehicle.descriptor.type.crewRoles ]
            for slot, recruit in enumerate(lastRecruits):
                recruitBlockedState = None
                if recruit is None:
                    recruitBlockedState = self.__getActualWarning(reason, PREV_CREW_WARNING_DEMOBILIZED)
                    reason = recruitBlockedState if recruitBlockedState else reason
                    continue
                if recruit.role != crewRoles[slot]:
                    recruitBlockedState = self.__getActualWarning(reason, PREV_CREW_WARNING_RETRAINED)
                currentRecruitVehicle = self.itemsCache.items.getVehicle(recruit.vehicleInvID)
                if currentRecruitVehicle:
                    if currentRecruitVehicle.isInBattle:
                        recruitBlockedState = self.__getActualWarning(reason, PREV_CREW_WARNING_MEMBERS_IN_BATTLE)
                reason = recruitBlockedState if recruitBlockedState else reason
                if recruit.invID not in currentCrew and not recruitBlockedState:
                    isOpAvailable = True

            return self.__getInitCrewOperationObject(OPERATION_RETURN, reason, warning=True, available=isOpAvailable) if reason else self.__getInitCrewOperationObject(OPERATION_RETURN)

    def __getRetrainOperationData(self, vehicle):
        crew = vehicle.crew
        if vehicle.isDisabled:
            return self.__getInitCrewOperationObject(OPERATION_RETRAIN, 'locked')
        if self.__isCrewMissing(crew):
            return self.__getInitCrewOperationObject(OPERATION_RETRAIN, 'noCrew')
        return self.__getInitCrewOperationObject(OPERATION_RETRAIN, 'alreadyRetrained') if self.__isNativeCrewForCurrentVehicle(crew, vehicle) else self.__getInitCrewOperationObject(OPERATION_RETRAIN)

    def __getDropInBarrackOldCrewOperationData(self):
        return self.__getInitCrewOperationObject(OPERATION_DROP_IN_BARRACK_OLD_CREW)

    def __getActualWarning(self, status, warning):
        return warning if not status or status == warning else PREV_CREW_WARNING_COMPOUND

    def __isCrewMissing(self, crew):
        return all((tman is None for _, tman in crew))

    def __isNativeCrewForCurrentVehicle(self, crew, vehicle):
        return all((tman.vehicleNativeDescr.type.compactDescr == vehicle.intCD for _, tman in crew if tman))

    def __getAvailableRecruits(self, nationID):
        items = self.itemsCache.items
        criteria = REQ_CRITERIA.TANKMAN.ACTIVE | ~REQ_CRITERIA.TANKMAN.DISMISSED | REQ_CRITERIA.NATIONS([nationID]) | ~REQ_CRITERIA.TANKMAN.IN_TANK
        excludeCriteria = ~REQ_CRITERIA.VEHICLE.LOCKED | ~REQ_CRITERIA.VEHICLE.HAS_TAGS([VEHICLE_TAGS.CREW_LOCKED])
        excludeCriteria |= ~REQ_CRITERIA.VEHICLE.BATTLE_ROYALE | ~REQ_CRITERIA.VEHICLE.EVENT_BATTLE
        dirtyRecruits = items.getTankmen(criteria)
        suitableRecruits = items.removeUnsuitableTankmen(dirtyRecruits.itervalues(), excludeCriteria)
        return len(suitableRecruits)

    def invokeOperation(self, operationName):
        if operationName == OPERATION_RETRAIN:
            g_detachmentFlowLogger.flow(self.uiDetachmentLogger.group, GROUP.RETRAIN_CREW_DIALOG)
            self.fireEvent(LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.RETRAIN_CREW)), EVENT_BUS_SCOPE.LOBBY)
        elif operationName == OPERATION_RETURN:
            self.uiDetachmentLogger.log(ACTION.RETURN_PREVIOUS_RECRUIT_CONFIGURATION)
            self.fireEvent(events.CrewPanelEvent(events.CrewPanelEvent.RETURN_RECRUITS), scope=EVENT_BUS_SCOPE.LOBBY)
        elif operationName == OPERATION_SET_BEST_CREW:
            self.uiDetachmentLogger.log(ACTION.SELECT_BEST_RECRUITS)
            AccountSettings.setSettings(BEST_CREW_OPTION_USED, True)
            self.fireEvent(events.CrewPanelEvent(events.CrewPanelEvent.SET_BEST_RECRUITS, ctx={'isNative': False}), scope=EVENT_BUS_SCOPE.LOBBY)
        elif operationName == OPERATION_DROP_IN_BARRACK_OLD_CREW:
            self.uiDetachmentLogger.log(ACTION.UNLOAD_ALL_RECRUITS)
            self.fireEvent(events.CrewPanelEvent(events.CrewPanelEvent.UNLOAD_RECRUITS), scope=EVENT_BUS_SCOPE.LOBBY)

    def __getInitCrewOperationObject(self, operationId, errorId=None, warning=False, available=False, hintValue=''):
        iconPathContext = '../maps/icons/tankmen/crew/%s%s'
        iconPath = iconPathContext % (operationId, '.png')
        msgType = 'warning' if warning else 'error'
        state = 'enabled' if available else 'disabled'
        cOpId = R.strings.crew_operations.dyn(operationId)
        errorText = backport.text(cOpId.dyn(msgType).dyn(errorId)()) if errorId and not available else ''
        tooltipText = backport.text(cOpId.dyn(msgType).tooltip.dyn(state).dyn(errorId)()) if errorId else ''
        titleText = backport.text(cOpId.title())
        description = backport.text(cOpId.description())
        warningInfo = {'operationAvailable': available} if warning else None
        return {'id': operationId,
         'iconPath': iconPath,
         'title': titleText,
         'description': description,
         'hint': hintValue,
         'error': errorText,
         'warning': warningInfo,
         'tooltip': tooltipText}

    def __unitMgrOnUnitLeft(self, _):
        self._destroy()
