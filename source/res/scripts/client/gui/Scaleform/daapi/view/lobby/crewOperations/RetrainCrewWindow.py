# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/crewOperations/RetrainCrewWindow.py
from CurrentVehicle import g_currentVehicle
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.meta.RetrainCrewWindowMeta import RetrainCrewWindowMeta
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.gui_items import Tankman
from gui.shared.gui_items.processors.tankman import TankmanCrewRetraining
from gui.shared.gui_items.serializers import packTraining
from gui.shared.money import Money, Currency
from gui.shared.utils import decorators
from gui.shared.utils.functions import makeTooltip
from gui.shop import showBuyGoldForCrew
from helpers import dependency
from skeletons.gui.shared import IItemsCache

class RetrainCrewWindow(RetrainCrewWindowMeta):
    AVAILABLE_OPERATIONS = range(3)
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, ctx=None):
        super(RetrainCrewWindow, self).__init__()
        self.__vehicle = vehicle = ctx.get('vehicle', g_currentVehicle.item)
        self.__crew = ctx.get('crew', vehicle.crew)
        self.__callback = ctx.get('callback')

    def submit(self, operationId):
        if operationId in self.AVAILABLE_OPERATIONS:
            _, cost = self.getCrewTrainInfo(int(operationId))
            currentGold = self.itemsCache.items.stats.gold
            if currentGold < cost.get(Currency.GOLD, 0):
                showBuyGoldForCrew(cost.get(Currency.GOLD))
                return
            self.__processCrewRetrianing(operationId)

    def onWindowClose(self):
        self.destroy()

    def changeRetrainType(self, operationId):
        crew, cost = self.getCrewTrainInfo(int(operationId))
        currentMoney = self.itemsCache.items.stats.money
        isMoneyEnough = cost <= currentMoney
        enableSubmitButton = bool(crew and (isMoneyEnough or cost.get(Currency.GOLD)))
        self.as_setCrewDataS({'price': cost.toMoneyTuple(),
         'crew': crew,
         'crewMembersText': text_styles.concatStylesWithSpace(backport.text(R.strings.detachment.crew.retrain.amount()), text_styles.middleTitle(len(crew))),
         'enableSubmitButton': enableSubmitButton,
         'isMoneyEnough': isMoneyEnough})
        self.as_updateInfoIconTooltipDataS(self.__getInfoTooltipData(operationId))
        shortage = currentMoney.getShortage(cost)
        self.as_updateNotEnoughMoneyTooltipDataS(self.__getNotEnoughMoneyTooltipData(shortage))

    def getOperationCost(self, priceInfo, crewSize):
        return Money(credits=priceInfo[Currency.CREDITS] or None, gold=priceInfo[Currency.GOLD] or None) * crewSize

    def getCrewTrainInfo(self, operationID):
        items = self.itemsCache.items
        vehicle = self.__vehicle
        shopPrices = items.shop.tankmanCost
        currentSelection = shopPrices[operationID]
        crewInfo = [ self.__getTankmanRoleInfo(tMan) for _, tMan in self.__crew if tMan and tMan.vehicleNativeDescr.type.compactDescr != vehicle.intCD ]
        cost = self.getOperationCost(currentSelection, len(crewInfo))
        return (crewInfo, cost)

    def _populate(self):
        super(RetrainCrewWindow, self)._populate()
        g_clientUpdateManager.addMoneyCallback(self.__updateDataCallBack)
        g_currentVehicle.onChanged += self.__onCurrentVehicleChanged
        g_clientUpdateManager.addCallbacks({'shop': self.__updateDataCallBack()})
        self.__updateAllData()

    def __updateAllData(self):
        isPremium = self.__vehicle.isPremium or self.__vehicle.isPremiumIGR
        warningText = backport.text(R.strings.detachment.crew.recruit.toPremiumVehicle.description()) if isPremium else ''
        tooltip = {'tooltip': makeTooltip(backport.text(R.strings.detachment.crew.recruit.toPremiumVehicle.tooltip.header()), backport.text(R.strings.detachment.crew.recruit.toPremiumVehicle.tooltip.body())) if isPremium else ''}
        self.as_setVehicleDataS({'nationID': self.__vehicle.nationID,
         'vType': self.__vehicle.type,
         'vIntCD': self.__vehicle.intCD,
         'vLevel': self.__vehicle.level,
         'vName': self.__vehicle.shortUserName,
         'vIconSmall': self.__vehicle.iconSmall,
         'warningText': warningText,
         'warningTooltip': tooltip})
        self.__updateDataCallBack()

    @property
    def crew(self):
        return [ tMan for _, tMan in self.__crew if tMan and tMan.vehicleNativeDescr.type.compactDescr != self.__vehicle.intCD ]

    def _dispose(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        g_currentVehicle.onChanged -= self.__onCurrentVehicleChanged
        super(RetrainCrewWindow, self)._dispose()

    def __updateDataCallBack(self, data=None):
        items = self.itemsCache.items
        shopPrices, _ = items.shop.getTankmanCostWithDefaults()
        retrainButtons = packTraining(self.__vehicle, self.crew)
        for operationID, button in enumerate(retrainButtons):
            if not button['penalty']:
                button['tooltip'] = {'tooltip': makeTooltip(backport.text(R.strings.detachment.crew.recruit.retrain.warning.tooltip.header()), backport.text(R.strings.detachment.crew.recruit.retrain.warning.tooltip.body()))}
            button['tooltip'] = self.__getInfoTooltipData(operationID)

        data = {'credits': items.stats.credits,
         'gold': items.stats.gold,
         'tankmanCost': shopPrices,
         'retrainButtons': retrainButtons,
         'infoTooltip': self.__getInfoTooltipData()}
        self.as_setCrewOperationDataS(data)

    def __getInfoTooltipData(self, operationID=0):
        retrainButtons = packTraining(self.__vehicle, self.crew)
        if retrainButtons[int(operationID)]['penalty']:
            specialArgs = [operationID, self.__vehicle.intCD, [ tMan.invID for tMan in self.crew ]]
            return {'isWulf': True,
             'specialAlias': TOOLTIPS_CONSTANTS.CREW_RETRAIN_PENALTY,
             'specialArgs': specialArgs}
        return {'tooltip': makeTooltip(backport.text(R.strings.detachment.crew.recruit.retrain.warning.tooltip.header()), backport.text(R.strings.detachment.crew.recruit.retrain.warning.tooltip.body()))}

    def __getNotEnoughMoneyTooltipData(self, shortage):
        if bool(shortage):
            currency = shortage.getCurrency()
            return {'isSpecial': True,
             'specialAlias': TOOLTIPS_CONSTANTS.NOT_ENOUGH_MONEY,
             'specialArgs': (shortage.get(currency), currency)}
        else:
            return None

    def __getTankmanRoleInfo(self, tankman):
        vehicle = self.itemsCache.items.getItemByCD(tankman.vehicleNativeDescr.type.compactDescr)
        return {'realRoleLevel': tankman.efficiencyRoleLevel,
         'roleLevel': tankman.roleLevel,
         'nativeVehicleType': vehicle.type,
         'nativeVehicleIntCD': vehicle.intCD,
         'tankmanID': tankman.invID,
         'nationID': tankman.nationID,
         'iconPath': Tankman.getRoleMediumIconPath(tankman.descriptor.role)}

    @decorators.process('crewRetraining')
    def __processCrewRetrianing(self, operationId):
        vehicle = self.__vehicle
        crewInvIDs = [ tMan.invID for _, tMan in self.__crew if tMan and tMan.vehicleNativeDescr.type.compactDescr != vehicle.intCD ]
        result = yield TankmanCrewRetraining(crewInvIDs, vehicle, operationId).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
        if self.__callback:
            self.__callback()
        if result.success:
            self.destroy()

    def __onCurrentVehicleChanged(self):
        self.__vehicle = g_currentVehicle.item
        if not self.__vehicle or self.__vehicle.isOnlyForBattleRoyaleBattles:
            self.destroy()
        else:
            self.__updateAllData()
