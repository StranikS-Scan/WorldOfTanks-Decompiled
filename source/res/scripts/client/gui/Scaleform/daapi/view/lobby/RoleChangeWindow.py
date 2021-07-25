# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/RoleChangeWindow.py
from typing import Optional
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.meta.RoleChangeMeta import RoleChangeMeta
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.auxiliary.detachment_helper import removeUnsuitableRecruits
from gui.impl.gen import R
from gui.shared.formatters import icons, text_styles
from gui.shared.gui_items import Tankman
from gui.shared.gui_items.crew_skin import getCrewSkinIconBig
from gui.shared.gui_items.crew_skin import localizedFullName
from gui.shared.gui_items.processors.tankman import TankmanChangeRole, TankmanRetraining
from gui.shared.gui_items.serializers import packTankman, packTraining
from gui.shared.money import Currency
from gui.shared.money import Money
from gui.shared.tooltips import ACTION_TOOLTIPS_TYPE
from gui.shared.tooltips.formatters import packActionTooltipData
from gui.shared.utils import decorators
from gui.shared.utils.functions import makeTooltip
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from gui.shop import showBuyGoldForCrew
from helpers import dependency
from items.components.crew_skins_constants import NO_CREW_SKIN_ID
from nations import NAMES
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache

def _getTankmanVO(tankman):
    packedTankman = packTankman(tankman, isCountPermanentSkills=False)
    fullName = '%s %s' % (packedTankman['firstUserName'], packedTankman['lastUserName'])
    return {'tankmanID': tankman.invID,
     'name': fullName,
     'nation': NAMES[tankman.nationID],
     'rank': packedTankman['rankUserName'],
     'vehicle': packedTankman['nativeVehicle']['userName'],
     'vehicleIcon': packedTankman['nativeVehicle']['typeIconFlat'],
     'faceIcon': packedTankman['icon']['big'],
     'rankIcon': packedTankman['iconRank']['big'],
     'roleIcon': packedTankman['iconRole']['medium'],
     'role': packedTankman['roleUserName']}


class RetrainRoleChangeWindow(RoleChangeMeta):
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.instance(ILobbyContext)
    _GOLD_OPERATION = 2

    def __init__(self, ctx=None):
        super(RetrainRoleChangeWindow, self).__init__()
        self.__tankman = self.itemsCache.items.getTankman(ctx.get('tankmanID'))
        self.__nativeVehicleCD = self.__tankman.vehicleNativeDescr.type.compactDescr
        self.__requiredRole = ctx.get('requiredRole', self.__tankman.role)
        self.__operationID = 0
        self.__fromMobilizationWindow = ctx.get('mobilization', False)
        self.__callback = ctx.get('callback', None)
        self.__currentVehicleCD = ctx.get('currentVehicleCD', None)
        if self.__currentVehicleCD is None and self.__tankman.vehicleDescr is not None:
            self.__currentVehicleCD = self.__tankman.vehicleDescr.type.compactDescr
        self.__vehicle = self.itemsCache.items.getItemByCD(self.__currentVehicleCD)
        return

    def changeRetrainType(self, operationID):
        self.__operationID = int(operationID)
        self.__checkMoney()

    def submit(self):
        if self._isRoleChangeState():
            self.changeRole()
        else:
            self.retrainingTankman()

    @decorators.process('retraining')
    def retrainingTankman(self):
        tankmanCostTypeIdx = self.__operationID
        operationCost = self.itemsCache.items.shop.tankmanCost[tankmanCostTypeIdx].get('gold', 0)
        currentGold = self.itemsCache.items.stats.gold
        if currentGold < operationCost:
            showBuyGoldForCrew(operationCost)
            return
        result = yield TankmanRetraining(self.__tankman, self.__vehicle, tankmanCostTypeIdx).request()
        SystemMessages.pushMessages(result)
        if self.__callback:
            self.__callback(result)
        if result.success:
            self.destroy()

    @decorators.process('changingRole')
    def changeRole(self, *args):
        changeRoleCost = self.itemsCache.items.shop.changeRoleCost
        actualGold = self.itemsCache.items.stats.gold
        if changeRoleCost > actualGold:
            showBuyGoldForCrew(changeRoleCost)
            return
        result = yield TankmanChangeRole(self.__tankman, self.__requiredRole, self.__currentVehicleCD).request()
        SystemMessages.pushMessages(result)
        if self.__callback:
            self.__callback(result)
        if result.success:
            self.destroy()

    def onWindowClose(self):
        self.destroy()

    def _populate(self):
        super(RetrainRoleChangeWindow, self)._populate()
        g_clientUpdateManager.addMoneyCallback(self._onMoneyUpdate)
        g_clientUpdateManager.addCallbacks({'shop': self._onStatsUpdate})
        self._onStatsUpdate()

    def _dispose(self):
        self.__tankman = None
        self.__currentVehicleCD = None
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(RetrainRoleChangeWindow, self)._dispose()
        return

    def _onMoneyUpdate(self, *args):
        self.__checkMoney()
        if self._isRoleChangeState():
            self.__setRoleData()
        else:
            self.__setCrewOperationData()

    def _isRoleChangeState(self):
        return self.__tankman.role != self.__requiredRole

    def _onStatsUpdate(self, *args):
        self.__setCommonData()
        self.__setVehicleData()
        if self._isRoleChangeState():
            self.__setRoleData()
        else:
            self.__setCrewOperationData()

    def __checkMoney(self):
        items = self.itemsCache.items
        discount = None
        notEnoughMoneyTooltip = None
        if self._isRoleChangeState():
            changeRoleCost = items.shop.changeRoleCost
            actualCurrency = Currency.GOLD
            defaultChangeRoleCost = items.shop.defaults.changeRoleCost
            if changeRoleCost != defaultChangeRoleCost:
                discount = packActionTooltipData(ACTION_TOOLTIPS_TYPE.ECONOMICS, 'changeRoleCost', True, Money(gold=changeRoleCost), Money(gold=defaultChangeRoleCost))
            formattedPrice = backport.getIntegralFormat(changeRoleCost)
            shortage = changeRoleCost - items.stats.gold
            style = text_styles.gold if shortage <= 0 else text_styles.error
            icon = icons.gold()
            enableSubmitButton = True
        else:
            tankmanCost = items.shop.tankmanCost[self.__operationID]
            isGoldOperation = self.__operationID == self._GOLD_OPERATION
            if isGoldOperation:
                retrainCost = tankmanCost[Currency.GOLD]
                actualCurrency = Currency.GOLD
                actualMoney = items.stats.gold
                style = text_styles.gold
                icon = icons.gold()
            else:
                retrainCost = tankmanCost[Currency.CREDITS]
                actualCurrency = Currency.CREDITS
                actualMoney = items.stats.credits
                style = text_styles.credits
                icon = icons.credits()
            shortage = retrainCost - actualMoney
            if shortage > 0:
                style = text_styles.error
            formattedPrice = backport.getIntegralFormat(retrainCost)
            enableSubmitButton = shortage <= 0 or isGoldOperation
        if shortage > 0:
            notEnoughMoneyTooltip = {'isSpecial': True,
             'specialAlias': TOOLTIPS_CONSTANTS.NOT_ENOUGH_MONEY,
             'specialArgs': (shortage, actualCurrency)}
        self.as_setPriceS(priceString='{}{}'.format(style(formattedPrice), icon), actionChangeRole=discount, enableSubmitButton=enableSubmitButton, tooltip=notEnoughMoneyTooltip)
        return

    def __setCommonData(self):
        commonData = {'tankmanModel': _getTankmanVO(self.__tankman)}
        self.__updateIconForCrewSkin(commonData)
        self.as_setCommonDataS(commonData)

    def __setRoleData(self):
        if self.__fromMobilizationWindow:
            if self.__tankman.isInTank:
                place = R.strings.detachment.crew.recruit.changeRole.mob_description.in_tank()
                vehicle = self.itemsCache.items.getItemByCD(self.__tankman.vehicleDescr.type.compactDescr)
            else:
                place = R.strings.detachment.crew.recruit.changeRole.mob_description.in_barrack()
                vehicle = self.itemsCache.items.getItemByCD(self.__nativeVehicleCD)
            infoText = backport.text(place, vehicleName=vehicle.shortUserName, role=Tankman.getRoleUserName(self.__tankman.role))
        else:
            infoText = backport.text(R.strings.detachment.crew.recruit.changeRole.description(), vehicleName=self.__vehicle.shortUserName)
        tankmenCriteria = REQ_CRITERIA.TANKMAN.ACTIVE | REQ_CRITERIA.CUSTOM(lambda t: t.vehicleNativeDescr.type.compactDescr == self.__currentVehicleCD and t.role == self.__requiredRole)
        allTankmen = self.itemsCache.items.getTankmen(tankmenCriteria)
        suitableTmenCnt = len(removeUnsuitableRecruits(allTankmen, self.__vehicle))
        isWarningActive = suitableTmenCnt > 0
        roleData = {'name': Tankman.getRoleUserName(self.__requiredRole),
         'icon': Tankman.getRole42x42IconPath(self.__requiredRole),
         'isWarningActive': isWarningActive}
        if isWarningActive:
            roleData['warningHeader'] = backport.text(R.strings.tooltips.RoleChange.roleTaken.header())
            roleData['warningBody'] = backport.text(R.strings.tooltips.RoleChange.roleTaken.body(), number=suitableTmenCnt, vehicleName=self.__vehicle.shortUserName)
        self.as_setRoleS(roleData, infoText)

    def __setVehicleData(self):
        vehicle = self.__vehicle
        isPremium = vehicle.isPremium or vehicle.isPremiumIGR
        warningText = backport.text(R.strings.detachment.crew.recruit.toPremiumVehicle.description()) if isPremium else ''
        tooltip = {'tooltip': makeTooltip(backport.text(R.strings.detachment.crew.recruit.toPremiumVehicle.tooltip.header()), backport.text(R.strings.detachment.crew.recruit.toPremiumVehicle.tooltip.body())) if isPremium else ''}
        self.as_setVehicleDataS({'nationID': vehicle.nationID,
         'vType': vehicle.type,
         'vIntCD': vehicle.intCD,
         'vLevel': vehicle.level,
         'vName': vehicle.shortUserName,
         'vIconSmall': vehicle.iconSmall,
         'warningText': warningText,
         'warningTooltip': tooltip})

    def __setCrewOperationData(self):
        items = self.itemsCache.items
        shopPrices, _ = self.itemsCache.items.shop.getTankmanCostWithDefaults()
        tooltip = makeTooltip(backport.text(R.strings.detachment.crew.recruit.retrain.warning.tooltip.header()), backport.text(R.strings.detachment.crew.recruit.retrain.warning.tooltip.body()))
        retrainButtons = packTraining(self.__vehicle, [self.__tankman])
        for button in retrainButtons:
            button['tooltip'] = {'tooltip': tooltip}

        data = {'credits': items.stats.credits,
         'gold': items.stats.gold,
         'tankmanCost': shopPrices,
         'retrainButtons': retrainButtons,
         'infoTooltip': {'tooltip': tooltip}}
        self.as_setCrewOperationDataS(data)

    def __updateIconForCrewSkin(self, commonData):
        skinID = self.__tankman.skinID
        if skinID != NO_CREW_SKIN_ID and self.lobbyContext.getServerSettings().isCrewSkinsEnabled():
            skinItem = self.itemsCache.items.getCrewSkin(skinID)
            commonData['tankmanModel']['faceIcon'] = getCrewSkinIconBig(skinItem.getIconID())
            commonData['tankmanModel']['name'] = localizedFullName(skinItem)
