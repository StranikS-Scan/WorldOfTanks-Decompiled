# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/crewOperations/RetrainCrewWindow.py
from CurrentVehicle import g_currentVehicle
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.meta.RetrainCrewWindowMeta import RetrainCrewWindowMeta
from gui.shared.gui_items.processors.tankman import TankmanCrewRetraining
from gui.shared.utils import decorators
from gui.shared.money import Money
from gui import SystemMessages
from helpers import dependency
from items import tankmen
from gui.shared.formatters import text_styles
from helpers.i18n import makeString as _ms
from gui.Scaleform.locale.RETRAIN_CREW import RETRAIN_CREW
from skeletons.gui.shared import IItemsCache

class RetrainCrewWindow(RetrainCrewWindowMeta):
    AVAILABLE_OPERATIONS = range(3)
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, ctx=None):
        super(RetrainCrewWindow, self).__init__()
        self.__vehicle = g_currentVehicle.item
        self.__crew = []
        for idx, tMan in self.__vehicle.crew:
            if tMan is not None:
                if tMan.vehicleNativeDescr.type.compactDescr != tMan.vehicleDescr.type.compactDescr:
                    self.__crew.append(tMan)
                elif tMan.efficiencyRoleLevel < tankmen.MAX_SKILL_LEVEL:
                    self.__crew.append(tMan)

        return

    def _populate(self):
        super(RetrainCrewWindow, self)._populate()
        g_clientUpdateManager.addMoneyCallback(self.__updateDataCallBack)
        crewInfo = map(self.__getTankmanRoleInfo, self.__crew)
        self.as_setVehicleDataS({'nationID': self.__vehicle.nationID,
         'vType': self.__vehicle.type,
         'vIntCD': self.__vehicle.intCD,
         'vLevel': self.__vehicle.level,
         'vName': self.__vehicle.shortUserName,
         'vIconSmall': self.__vehicle.iconSmall})
        self.as_setAllCrewDataS({'crew': crewInfo})
        self.__updateDataCallBack()

    def __updateDataCallBack(self, data=None):
        items = self.itemsCache.items
        shopPrices, actionPrc = items.shop.getTankmanCostWithDefaults()
        skillValues = []
        for cost in shopPrices:
            minValue = maxValue = cost['roleLevel']
            baseRolleLoss = cost['baseRoleLoss']
            classChangeRoleLoss = cost['classChangeRoleLoss']
            for tankman in self.__crew:
                currentRoleLevel = tankman.roleLevel
                if tankman.areClassesCompatible:
                    roleValue = currentRoleLevel - currentRoleLevel * classChangeRoleLoss
                else:
                    roleValue = currentRoleLevel - currentRoleLevel * baseRolleLoss
                if roleValue > maxValue:
                    maxValue = int(round(roleValue))

            skillValues.append((minValue, maxValue))

        data = {'credits': items.stats.credits,
         'gold': items.stats.gold,
         'actionPrc': actionPrc,
         'tankmanCost': shopPrices}
        self.as_setCrewOperationDataS(data)

    def __getTankmanRoleInfo(self, tankman):
        vehicle = self.itemsCache.items.getItemByCD(tankman.vehicleNativeDescr.type.compactDescr)
        return {'realRoleLevel': tankman.efficiencyRoleLevel,
         'roleLevel': tankman.roleLevel,
         'nativeVehicleType': vehicle.type,
         'nativeVehicleIntCD': vehicle.intCD,
         'tankmanID': tankman.invID,
         'nationID': tankman.nationID,
         'iconPath': '../maps/icons/tankmen/roles/medium/%s' % tankman.iconRole}

    def submit(self, operationId):
        if operationId in self.AVAILABLE_OPERATIONS:
            self.__processCrewRetrianing(operationId)
            self.destroy()

    @decorators.process('crewRetraining')
    def __processCrewRetrianing(self, operationId):
        items = self.itemsCache.items
        vehicle = g_currentVehicle.item
        shopPrices = items.shop.tankmanCost
        currentSelection = shopPrices[operationId]
        crewInvIDs = []
        for idx, tMan in vehicle.crew:
            if tMan is not None:
                if tMan.vehicleNativeDescr.type.compactDescr != tMan.vehicleDescr.type.compactDescr:
                    crewInvIDs.append(tMan.invID)
                elif tMan.roleLevel != tankmen.MAX_SKILL_LEVEL and tMan.efficiencyRoleLevel < currentSelection['roleLevel']:
                    crewInvIDs.append(tMan.invID)

        result = yield TankmanCrewRetraining(crewInvIDs, vehicle, operationId).request()
        if len(result.userMsg):
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
        return

    def onWindowClose(self):
        self.destroy()

    def changeRetrainType(self, operationId):
        operationId = int(operationId)
        items = self.itemsCache.items
        vehicle = g_currentVehicle.item
        shopPrices = items.shop.tankmanCost
        currentSelection = shopPrices[operationId]
        crewInfo = []
        for idx, tMan in vehicle.crew:
            if tMan is not None:
                if tMan.vehicleNativeDescr.type.compactDescr != tMan.vehicleDescr.type.compactDescr:
                    crewInfo.append(self.__getTankmanRoleInfo(tMan))
                elif tMan.roleLevel != tankmen.MAX_SKILL_LEVEL and tMan.efficiencyRoleLevel < currentSelection['roleLevel']:
                    crewInfo.append(self.__getTankmanRoleInfo(tMan))

        crewSize = len(crewInfo)
        price = crewSize * Money(**currentSelection)
        self.as_setCrewDataS({'price': price,
         'crew': crewInfo,
         'crewMembersText': text_styles.concatStylesWithSpace(_ms(RETRAIN_CREW.LABEL_CREWMEMBERS), text_styles.middleTitle(crewSize))})
        return

    def _dispose(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(RetrainCrewWindow, self)._dispose()
