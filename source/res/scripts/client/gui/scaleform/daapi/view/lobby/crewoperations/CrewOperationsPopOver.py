# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/crewOperations/CrewOperationsPopOver.py
from CurrentVehicle import g_currentVehicle
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.hangar.Crew import Crew
from gui.Scaleform.daapi.view.meta.CrewOperationsPopOverMeta import CrewOperationsPopOverMeta
from gui.Scaleform.locale.CREW_OPERATIONS import CREW_OPERATIONS
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.events import LoadViewEvent
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Tankman import TankmenComparator
from gui.shared.gui_items.processors.tankman import TankmanReturn
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from helpers import dependency
from helpers import i18n
from gui.shared.utils import decorators
from gui import SystemMessages
from items import tankmen
from skeletons.gui.shared import IItemsCache
OPERATION_RETRAIN = 'retrain'
OPERATION_RETURN = 'return'
OPERATION_DROP_IN_BARRACK = 'dropInBarrack'

class CrewOperationsPopOver(CrewOperationsPopOverMeta):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, _=None):
        super(CrewOperationsPopOver, self).__init__()

    def _populate(self):
        super(CrewOperationsPopOver, self)._populate()
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
        return self.__getInitCrewOperationObject(OPERATION_RETRAIN, 'alreadyRetrained') if self.__isTopCrewForCurrentVehicle(crew, vehicle) else self.__getInitCrewOperationObject(OPERATION_RETRAIN)

    def __getReturnOperationData(self, vehicle):
        crew = vehicle.crew
        lastCrewIDs = vehicle.lastCrew
        tmen = self.itemsCache.items.getTankmen().values()
        berths = self.itemsCache.items.stats.tankmenBerthsCount
        tankmenInBarracks = 0
        for tankman in sorted(tmen, TankmenComparator(self.itemsCache.items.getVehicle)):
            if not tankman.isInTank:
                tankmenInBarracks += 1

        freeBerths = berths - tankmenInBarracks
        tankmenToBarracksCount = 0
        for tankman in crew:
            if tankman[1] is not None:
                tankmenToBarracksCount += 1

        demobilizedMembersCounter = 0
        isCrewAlreadyInCurrentVehicle = True
        if lastCrewIDs is not None:
            for lastTankmenInvID in lastCrewIDs:
                actualLastTankman = self.itemsCache.items.getTankman(lastTankmenInvID)
                if actualLastTankman is not None:
                    if actualLastTankman.isInTank:
                        lastTankmanVehicle = self.itemsCache.items.getVehicle(actualLastTankman.vehicleInvID)
                        if lastTankmanVehicle:
                            if lastTankmanVehicle.isLocked:
                                return self.__getInitCrewOperationObject(OPERATION_RETURN, None, CREW_OPERATIONS.RETURN_WARNING_MEMBERSINBATTLE_TOOLTIP)
                            if lastTankmanVehicle.invID != vehicle.invID:
                                isCrewAlreadyInCurrentVehicle = False
                            elif lastTankmanVehicle.invID == vehicle.invID:
                                tankmenToBarracksCount -= 1
                    else:
                        isCrewAlreadyInCurrentVehicle = False
                demobilizedMembersCounter += 1

            if tankmenToBarracksCount > freeBerths:
                return self.__getInitCrewOperationObject(OPERATION_RETURN, None, CREW_OPERATIONS.DROPINBARRACK_WARNING_NOSPACE_TOOLTIP)
        else:
            return self.__getInitCrewOperationObject(OPERATION_RETURN, 'noPrevious')
        if demobilizedMembersCounter > 0 and demobilizedMembersCounter == len(lastCrewIDs):
            return self.__getInitCrewOperationObject(OPERATION_RETURN, 'allDemobilized')
        elif isCrewAlreadyInCurrentVehicle:
            return self.__getInitCrewOperationObject(OPERATION_RETURN, 'alreadyOnPlaces')
        else:
            return self.__getInitCrewOperationObject(OPERATION_RETURN, None, CREW_OPERATIONS.RETURN_WARNING_MEMBERDEMOBILIZED_TOOLTIP, True) if demobilizedMembersCounter > 0 and demobilizedMembersCounter < len(lastCrewIDs) else self.__getInitCrewOperationObject(OPERATION_RETURN)

    def __getDropInBarrackOperationData(self, vehicle):
        crew = vehicle.crew
        if self.__isNoCrew(crew):
            return self.__getInitCrewOperationObject(OPERATION_DROP_IN_BARRACK, 'noCrew')
        else:
            return self.__getInitCrewOperationObject(OPERATION_DROP_IN_BARRACK, None, CREW_OPERATIONS.DROPINBARRACK_WARNING_NOSPACE_TOOLTIP) if self.__isNotEnoughSpaceInBarrack(crew) else self.__getInitCrewOperationObject(OPERATION_DROP_IN_BARRACK)

    def __isTopCrewForCurrentVehicle(self, crew, vehicle):
        for _, tman in crew:
            if tman is not None:
                if tman.efficiencyRoleLevel < tankmen.MAX_SKILL_LEVEL or tman.vehicleNativeDescr.type.compactDescr != vehicle.intCD and not vehicle.isPremium:
                    return False

        return True

    def __isNoCrew(self, crew):
        for _, tman in crew:
            if tman is not None:
                return False

        return True

    def __isNotEnoughSpaceInBarrack(self, crew):
        berthsNeeded = len([ (role, t) for role, t in crew if t is not None ])
        barracksTmen = self.itemsCache.items.getTankmen(~REQ_CRITERIA.TANKMAN.IN_TANK | REQ_CRITERIA.TANKMAN.ACTIVE)
        tmenBerthsCount = self.itemsCache.items.stats.tankmenBerthsCount
        return berthsNeeded > 0 and berthsNeeded > tmenBerthsCount - len(barracksTmen)

    def invokeOperation(self, operationName):
        if operationName == OPERATION_RETRAIN:
            self.fireEvent(LoadViewEvent(VIEW_ALIAS.RETRAIN_CREW), EVENT_BUS_SCOPE.LOBBY)
        elif operationName == OPERATION_RETURN:
            self.__processReturnCrew()
        else:
            Crew.unloadCrew()

    @decorators.process('crewReturning')
    def __processReturnCrew(self):
        result = yield TankmanReturn(g_currentVehicle.item).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    def __getInitCrewOperationObject(self, operationId, errorId=None, warningId='', operationAvailable=False):
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
