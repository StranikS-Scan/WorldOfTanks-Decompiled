# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/crewOperations/CrewOperationsPopOver.py
from CurrentVehicle import g_currentVehicle
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.lobby.hangar.Crew import Crew
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView
from gui.Scaleform.daapi.view.meta.CrewOperationsPopOverMeta import CrewOperationsPopOverMeta
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.locale.CREW_OPERATIONS import CREW_OPERATIONS
from gui.shared import g_itemsCache
from gui.shared.events import ShowWindowEvent
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.processors.tankman import TankmanReturn
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from helpers import i18n
from gui.shared.utils import decorators
from gui import SystemMessages
OPERATION_RETRAIN = 'retrain'
OPERATION_RETURN = 'return'
OPERATION_DROP_IN_BARRACK = 'dropInBarrack'

class CrewOperationsPopOver(CrewOperationsPopOverMeta, View, SmartPopOverView):

    def __init__(self, ctx):
        super(CrewOperationsPopOver, self).__init__()

    def _populate(self):
        super(CrewOperationsPopOverMeta, self)._populate()
        g_clientUpdateManager.addCallbacks({'inventory': self.onInventoryUpdate})
        self.__update()

    def onInventoryUpdate(self, invDiff):
        if GUI_ITEM_TYPE.TANKMAN in invDiff:
            self.__update()

    def __update(self):
        vehicle = g_currentVehicle.item
        dataForUpdate = {'operationsArray': (self.__getRetrainOperationData(vehicle), self.__getReturnOperationData(vehicle), self.__getDropInBarrackOperationData(vehicle))}
        self.as_updateS(dataForUpdate)

    def __getRetrainOperationData(self, vehicle):
        crew = vehicle.crew
        if self.__isNoCrew(crew):
            return self.__getInitCrewOperationObject(OPERATION_RETRAIN, 'noCrew')
        if self.__isHasNotNative(crew) is not True:
            return self.__getInitCrewOperationObject(OPERATION_RETRAIN, 'alreadyRetrained')
        return self.__getInitCrewOperationObject(OPERATION_RETRAIN)

    def __getReturnOperationData(self, vehicle):
        crew = vehicle.crew
        lastCrewIDs = vehicle.lastCrew
        demobilizedMembersCounter = 0
        isCrewAlreadyInCurrentVehicle = True
        if lastCrewIDs is not None:
            for i in xrange(len(lastCrewIDs)):
                lastTankmenInvID = lastCrewIDs[i]
                actualLastTankman = g_itemsCache.items.getTankman(lastTankmenInvID)
                if actualLastTankman is not None:
                    if actualLastTankman.isInTank:
                        lastTankmanVehicle = g_itemsCache.items.getVehicle(actualLastTankman.vehicleInvID)
                        if lastTankmanVehicle:
                            if lastTankmanVehicle.isLocked:
                                return self.__getInitCrewOperationObject(OPERATION_RETURN, None, CREW_OPERATIONS.RETURN_WARNING_MEMBERSINBATTLE_TOOLTIP)
                            if lastTankmanVehicle.invID != vehicle.invID:
                                isCrewAlreadyInCurrentVehicle = False
                    else:
                        isCrewAlreadyInCurrentVehicle = False
                else:
                    demobilizedMembersCounter += 1

        else:
            return self.__getInitCrewOperationObject(OPERATION_RETURN, 'noPrevious')
        if demobilizedMembersCounter > 0 and demobilizedMembersCounter == len(lastCrewIDs):
            return self.__getInitCrewOperationObject(OPERATION_RETURN, 'allDemobilized')
        elif isCrewAlreadyInCurrentVehicle:
            return self.__getInitCrewOperationObject(OPERATION_RETURN, 'alreadyOnPlaces')
        elif self.__isNotEnoughSpaceInBarrack(crew):
            return self.__getInitCrewOperationObject(OPERATION_RETURN, None, CREW_OPERATIONS.RETURN_WARNING_NOSPACE_TOOLTIP)
        elif demobilizedMembersCounter > 0 and demobilizedMembersCounter < len(lastCrewIDs):
            return self.__getInitCrewOperationObject(OPERATION_RETURN, None, CREW_OPERATIONS.RETURN_WARNING_MEMBERDEMOBILIZED_TOOLTIP, True)
        else:
            return self.__getInitCrewOperationObject(OPERATION_RETURN)

    def __getDropInBarrackOperationData(self, vehicle):
        crew = vehicle.crew
        if self.__isNoCrew(crew):
            return self.__getInitCrewOperationObject(OPERATION_DROP_IN_BARRACK, 'noCrew')
        elif self.__isNotEnoughSpaceInBarrack(crew):
            return self.__getInitCrewOperationObject(OPERATION_DROP_IN_BARRACK, None, CREW_OPERATIONS.DROPINBARRACK_WARNING_NOSPACE_TOOLTIP)
        else:
            return self.__getInitCrewOperationObject(OPERATION_DROP_IN_BARRACK)

    def __isHasNotNative(self, crew):
        for slotIdx, tman in crew:
            if tman is not None:
                if tman.vehicleNativeDescr.type.compactDescr != tman.vehicleDescr.type.compactDescr:
                    return True
                if tman.realRoleLevel[0] < 100:
                    return True

        return False

    def __isNoCrew(self, crew):
        noCrew = True
        for slotIdx, tman in crew:
            if tman is not None:
                noCrew = False
                break

        return noCrew

    def __isNotEnoughSpaceInBarrack(self, crew):
        berthsNeeded = len(filter(lambda (role, t): t is not None, crew))
        barracksTmen = g_itemsCache.items.getTankmen(~REQ_CRITERIA.TANKMAN.IN_TANK)
        tmenBerthsCount = g_itemsCache.items.stats.tankmenBerthsCount
        return berthsNeeded > 0 and berthsNeeded > tmenBerthsCount - len(barracksTmen)

    def invokeOperation(self, operationName):
        if operationName == OPERATION_RETRAIN:
            self.fireEvent(ShowWindowEvent(ShowWindowEvent.SHOW_RETRAIN_CREW_WINDOW, {}))
        elif operationName == OPERATION_RETURN:
            self.__processReturnCrew()
        else:
            Crew.unloadCrew()

    @decorators.process('crewReturning')
    def __processReturnCrew(self):
        result = yield TankmanReturn(g_currentVehicle.item).request()
        if len(result.userMsg):
            SystemMessages.g_instance.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    def __getInitCrewOperationObject(self, operationId, errorId = None, warningId = '', operationAvailable = False):
        context = '#crew_operations:%s'
        cOpId = context % operationId
        iconPathContext = '../maps/icons/tankmen/crew/%s%s'
        errorText = ''
        btnLabelText = ''
        if errorId:
            errorText = i18n.makeString(cOpId + '/error/' + errorId)
        else:
            btnLabelText = i18n.makeString(cOpId + '/button/label')
        warningInfo = None
        if warningId != '':
            warningInfo = {'operationAvailable': operationAvailable,
             'tooltipId': warningId}
        return {'id': operationId,
         'iconPath': iconPathContext % (operationId, '.png'),
         'title': i18n.makeString(cOpId + '/title'),
         'description': i18n.makeString(cOpId + '/description'),
         'error': errorText,
         'warning': warningInfo,
         'btnLabel': btnLabelText}

    def onWindowClose(self):
        self.destroy()

    def _dispose(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(CrewOperationsPopOver, self)._dispose()
