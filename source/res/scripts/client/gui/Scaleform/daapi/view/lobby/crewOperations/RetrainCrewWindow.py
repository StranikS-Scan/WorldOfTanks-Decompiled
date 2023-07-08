# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/crewOperations/RetrainCrewWindow.py
from CurrentVehicle import g_currentVehicle
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.meta.RetrainCrewWindowMeta import RetrainCrewWindowMeta
from gui.impl import backport
from gui.impl.gen import R
from gui.shop import showBuyGoldForCrew
from gui.shared.gui_items.processors.tankman import TankmanCrewRetraining
from gui.shared.gui_items.serializers import packTraining
from gui.shared.utils import decorators
from gui.shared.money import Money, Currency
from gui import SystemMessages
from helpers import dependency
from items import tankmen
from gui.shared.formatters import text_styles
from skeletons.gui.shared import IItemsCache

class RetrainCrewWindow(RetrainCrewWindowMeta):
    AVAILABLE_OPERATIONS = range(3)
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, ctx=None):
        super(RetrainCrewWindow, self).__init__()
        self.__vehicle = g_currentVehicle.item
        self.__crew = []
        for _, tMan in self.__vehicle.crew:
            if tMan is not None:
                if tMan.vehicleNativeDescr.type.compactDescr != tMan.vehicleDescr.type.compactDescr:
                    self.__crew.append(tMan)
                elif tMan.efficiencyRoleLevel < tankmen.MAX_SKILL_LEVEL:
                    self.__crew.append(tMan)

        return

    def _populate(self):
        super(RetrainCrewWindow, self)._populate()
        g_clientUpdateManager.addMoneyCallback(self.__updateDataCallBack)
        g_clientUpdateManager.addCallbacks({'inventory.1.compDescr': self.__onVehiclesInInventoryUpdate})
        g_currentVehicle.onChanged += self.__onCurrentVehicleChanged
        self.__updateAllData()

    def submit(self, operationId):
        if operationId in self.AVAILABLE_OPERATIONS:
            _, cost = self.getCrewTrainInfo(int(operationId))
            currentGold = self.itemsCache.items.stats.gold
            if currentGold < cost.get(Currency.GOLD, 0):
                showBuyGoldForCrew(cost.get(Currency.GOLD))
                return
            self.__processCrewRetrianing(operationId)
            self.destroy()

    def onWindowClose(self):
        self.destroy()

    def changeRetrainType(self, operationId):
        crew, cost = self.getCrewTrainInfo(int(operationId))
        currentMoney = self.itemsCache.items.stats.money
        enableSubmitButton = bool(crew and (cost <= currentMoney or cost.get(Currency.GOLD)))
        self.as_setCrewDataS({'price': cost.toMoneyTuple(),
         'crew': crew,
         'crewMembersText': text_styles.concatStylesWithSpace(backport.text(R.strings.retrain_crew.label.crewMembers()), text_styles.middleTitle(len(crew))),
         'enableSubmitButton': enableSubmitButton})

    def getOperationCost(self, priceInfo, crewSize):
        return Money(credits=priceInfo[Currency.CREDITS] or None, gold=priceInfo[Currency.GOLD] or None) * crewSize

    def getCrewTrainInfo(self, operationID):
        items = self.itemsCache.items
        vehicle = g_currentVehicle.item
        shopPrices = items.shop.tankmanCost
        currentSelection = shopPrices[operationID]
        crewInfo = []
        for _, tMan in vehicle.crew:
            if tMan is not None:
                if tMan.vehicleNativeDescr.type.compactDescr != tMan.vehicleDescr.type.compactDescr:
                    crewInfo.append(self.__getTankmanRoleInfo(tMan))
                else:
                    currentRoleLevel = currentSelection['roleLevel']
                    if tMan.roleLevel != tankmen.MAX_SKILL_LEVEL and tMan.efficiencyRoleLevel < currentRoleLevel:
                        crewInfo.append(self.__getTankmanRoleInfo(tMan))

        cost = self.getOperationCost(currentSelection, len(crewInfo))
        return (crewInfo, cost)

    def _dispose(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        g_currentVehicle.onChanged -= self.__onCurrentVehicleChanged
        super(RetrainCrewWindow, self)._dispose()

    def __updateAllData(self):
        self.as_setVehicleDataS({'nationID': self.__vehicle.nationID,
         'vType': self.__vehicle.type,
         'vIntCD': self.__vehicle.intCD,
         'vLevel': self.__vehicle.level,
         'vName': self.__vehicle.shortUserName,
         'vIconSmall': self.__vehicle.iconSmall})
        self.__updateDataCallBack()

    def __updateDataCallBack(self, _=None):
        items = self.itemsCache.items
        shopPrices, _ = items.shop.getTankmanCostWithDefaults()
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
         'tankmanCost': shopPrices,
         'retrainButtons': packTraining(self.__vehicle, self.__crew)}
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

    @decorators.adisp_process('crewRetraining')
    def __processCrewRetrianing(self, operationId):
        items = self.itemsCache.items
        vehicle = g_currentVehicle.item
        shopPrices = items.shop.tankmanCost
        currentSelection = shopPrices[operationId]
        crewInvIDs = []
        for _, tMan in vehicle.crew:
            if tMan is not None:
                if tMan.vehicleNativeDescr.type.compactDescr != tMan.vehicleDescr.type.compactDescr:
                    crewInvIDs.append(tMan.invID)
                elif tMan.roleLevel != tankmen.MAX_SKILL_LEVEL and tMan.efficiencyRoleLevel < currentSelection['roleLevel']:
                    crewInvIDs.append(tMan.invID)

        result = yield TankmanCrewRetraining(crewInvIDs, vehicle, operationId).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
        return

    def __onCurrentVehicleChanged(self):
        self.__vehicle = g_currentVehicle.item
        if not self.__vehicle or self.__vehicle.isCrewLocked:
            self.destroy()
        else:
            self.__updateAllData()

    def __onVehiclesInInventoryUpdate(self, diff):
        if self.__vehicle.invID in diff and diff[self.__vehicle.invID] is None:
            self.onWindowClose()
        return
