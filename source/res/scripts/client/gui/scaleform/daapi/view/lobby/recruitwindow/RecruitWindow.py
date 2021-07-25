# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/recruitWindow/RecruitWindow.py
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.shop import showBuyGoldForCrew
from gui.shared.gui_items.serializers import packTraining
from gui.shared.tooltips import ACTION_TOOLTIPS_TYPE
import nations
import constants
from gui.Scaleform.locale.DIALOGS import DIALOGS
from gui.Scaleform.locale.MENU import MENU
from adisp import process, async
from helpers import dependency
from items.tankmen import getSkillsConfig
from helpers.i18n import convert
from gui import GUI_NATIONS, SystemMessages
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.view.meta.RecruitWindowMeta import RecruitWindowMeta
from gui.Scaleform.framework.entities.View import View
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared.utils import decorators
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.processors.tankman import TankmanRecruit, TankmanEquip, TankmanRecruitAndEquip
from gui.shared.money import Money, Currency
from gui.shared.tooltips.formatters import packActionTooltipData
from skeletons.gui.shared import IItemsCache

class RecruitWindow(RecruitWindowMeta):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, ctx=None):
        super(RecruitWindow, self).__init__()
        self._initData = ctx.get('data', None)
        self._menuEnabled = ctx.get('menuEnabled', False)
        self._currentVehicleInvId = ctx.get('currentVehicleId', None)
        return

    def _populate(self):
        View._populate(self)
        self.__getInitialData()
        if self._currentVehicleInvId != -1:
            g_clientUpdateManager.addCallbacks({'inventory': self.onInventoryChanged})
        g_clientUpdateManager.addCurrencyCallback(Currency.CREDITS, self.onCreditsChange)
        g_clientUpdateManager.addCurrencyCallback(Currency.GOLD, self.onGoldChange)
        g_clientUpdateManager.addCallbacks({'cache.mayConsumeWalletResources': self.onGoldChange})

    def onGoldChange(self, value):
        if self._currentVehicleInvId is not None:
            self.as_setRecruitButtonsEnableStateS(*self.__getRetrainButtonsEnableFlags())
        return

    def onCreditsChange(self, value):
        if self._currentVehicleInvId is not None:
            self.as_setRecruitButtonsEnableStateS(*self.__getRetrainButtonsEnableFlags())
        return

    def onInventoryChanged(self, inventory):
        if GUI_ITEM_TYPE.VEHICLE in inventory and 'compDescr' in inventory[GUI_ITEM_TYPE.VEHICLE]:
            changedVehicles = inventory[GUI_ITEM_TYPE.VEHICLE]['compDescr']
            if changedVehicles.get(self._currentVehicleInvId, None) is None:
                self._currentVehicleInvId = None
                self.onWindowClose()
        return

    def _dispose(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(RecruitWindow, self)._dispose()

    def __getInitialData(self):
        money = self.itemsCache.items.stats.money
        shop = self.itemsCache.items.shop
        upgradeParams = shop.tankmanCost
        defUpgradeParams = shop.defaults.tankmanCost
        schoolUpgradePrice = round(upgradeParams[1]['credits'])
        schoolUpgradeDefPrice = round(defUpgradeParams[1]['credits'])
        schoolUpgradeAction = None
        if schoolUpgradePrice != schoolUpgradeDefPrice:
            schoolUpgradeAction = packActionTooltipData(ACTION_TOOLTIPS_TYPE.ECONOMICS, 'creditsTankmanCost', True, Money(credits=schoolUpgradePrice), Money(credits=schoolUpgradeDefPrice))
        academyUpgradePrice = round(upgradeParams[2]['gold'])
        academyUpgradeDefPrice = round(defUpgradeParams[2]['gold'])
        academyUpgradeAction = None
        if academyUpgradePrice != academyUpgradeDefPrice:
            academyUpgradeAction = packActionTooltipData(ACTION_TOOLTIPS_TYPE.ECONOMICS, 'goldTankmanCost', True, Money(gold=academyUpgradePrice), Money(gold=academyUpgradeDefPrice))
        data = {Currency.CREDITS: money.getSignValue(Currency.CREDITS),
         Currency.GOLD: money.getSignValue(Currency.GOLD),
         'schoolUpgradePrice': schoolUpgradePrice,
         'schoolUpgradeActionPriceData': schoolUpgradeAction,
         'academyUpgradePrice': academyUpgradePrice,
         'academyUpgradeActionPriceData': academyUpgradeAction,
         'data': self._initData,
         'menuEnabled': self._menuEnabled}
        self.as_initDataS(data)
        self.as_setRecruitButtonsEnableStateS(*self.__getRetrainButtonsEnableFlags())
        return

    def __getRetrainButtonsEnableFlags(self):
        vehicle = self.itemsCache.items.getVehicle(self._currentVehicleInvId) if self._currentVehicleInvId is not None else None
        return [ option['enabled'] for option in reversed(packTraining(vehicle)) ]

    def updateAllDropdowns(self, nationID, tankType, typeID, roleType):
        nationsDP = [{'id': None,
          'label': DIALOGS.RECRUITWINDOW_MENUEMPTYROW}, {'id': nationID,
          'label': MENU.nations(nations.NAMES[int(nationID)])}]
        classesDP = [{'id': None,
          'label': DIALOGS.RECRUITWINDOW_MENUEMPTYROW}, {'id': tankType,
          'label': DIALOGS.recruitwindow_vehicleclassdropdown(tankType)}]
        typesDP = [{'id': None,
          'label': DIALOGS.RECRUITWINDOW_MENUEMPTYROW}]
        rolesDP = [{'id': None,
          'label': DIALOGS.RECRUITWINDOW_MENUEMPTYROW}]
        modulesAll = self.itemsCache.items.getVehicles(self.__getRoleCriteria(nationID, tankType, typeID)).values()
        modulesAll.sort()
        for module in modulesAll:
            typesDP.append({'id': module.innationID,
             'label': module.shortUserName})
            skillsConfig = getSkillsConfig()
            for role in module.descriptor.type.crewRoles:
                if role[0] == roleType:
                    rolesDP.append({'id': role[0],
                     'label': convert(skillsConfig.getSkill(role[0]).userString)})

            break

        self.flashObject.as_setAllDropdowns(nationsDP, classesDP, typesDP, rolesDP)
        return

    def __getNationsCriteria(self):
        rqc = REQ_CRITERIA
        criteria = ~(~rqc.UNLOCKED | ~rqc.COLLECTIBLE)
        criteria |= ~rqc.VEHICLE.OBSERVER
        criteria |= ~rqc.VEHICLE.BATTLE_ROYALE
        criteria |= ~rqc.VEHICLE.MAPS_TRAINING
        return criteria

    def updateNationDropdown(self):
        vehsItems = self.itemsCache.items.getVehicles(self.__getNationsCriteria())
        data = [{'id': None,
          'label': DIALOGS.RECRUITWINDOW_MENUEMPTYROW}]
        for name in GUI_NATIONS:
            nationIdx = nations.INDICES[name]
            vehiclesAvailable = len(vehsItems.filter(REQ_CRITERIA.NATIONS([nationIdx]))) > 0
            if name in nations.AVAILABLE_NAMES and vehiclesAvailable:
                data.append({'id': nationIdx,
                 'label': MENU.nations(name)})

        self.flashObject.as_setNations(data)
        return

    def __getClassesCriteria(self, nationID):
        maxResearchedLevel = self.itemsCache.items.stats.getMaxResearchedLevel(nationID)
        criteria = self.__getNationsCriteria() | REQ_CRITERIA.NATIONS([nationID])
        criteria |= ~(REQ_CRITERIA.COLLECTIBLE | ~REQ_CRITERIA.VEHICLE.LEVELS(range(1, maxResearchedLevel + 1)) | ~REQ_CRITERIA.INVENTORY)
        return criteria

    def updateVehicleClassDropdown(self, nationID):
        Waiting.show('updating')
        modulesAll = self.itemsCache.items.getVehicles(self.__getClassesCriteria(nationID)).values()
        classes = []
        data = [{'id': None,
          'label': DIALOGS.RECRUITWINDOW_MENUEMPTYROW}]
        modulesAll.sort()
        for module in modulesAll:
            if module.type in classes:
                continue
            classes.append(module.type)
            data.append({'id': module.type,
             'label': DIALOGS.recruitwindow_vehicleclassdropdown(module.type)})

        self.flashObject.as_setVehicleClassDropdown(data)
        Waiting.hide('updating')
        return

    def __getVehicleTypeCriteria(self, nationID, vclass):
        criteria = self.__getClassesCriteria(nationID) | REQ_CRITERIA.VEHICLE.CLASSES([vclass])
        criteria |= ~REQ_CRITERIA.VEHICLE.IS_CREW_LOCKED
        criteria |= ~(REQ_CRITERIA.SECRET | ~REQ_CRITERIA.INVENTORY_OR_UNLOCKED)
        if not constants.IS_IGR_ENABLED:
            criteria |= ~REQ_CRITERIA.VEHICLE.IS_PREMIUM_IGR
        if constants.IS_DEVELOPMENT:
            criteria |= ~REQ_CRITERIA.VEHICLE.IS_BOT
        return criteria

    def updateVehicleTypeDropdown(self, nationID, vclass):
        Waiting.show('updating')
        modulesAll = self.itemsCache.items.getVehicles(self.__getVehicleTypeCriteria(nationID, vclass)).values()
        data = [{'id': None,
          'label': DIALOGS.RECRUITWINDOW_MENUEMPTYROW}]
        modulesAll.sort()
        for module in modulesAll:
            data.append({'id': module.innationID,
             'label': module.shortUserName})

        self.flashObject.as_setVehicleTypeDropdown(data)
        Waiting.hide('updating')
        return

    def __getRoleCriteria(self, nationID, vclass, typeID):
        return self.__getVehicleTypeCriteria(nationID, vclass) | REQ_CRITERIA.INNATION_IDS([typeID])

    def updateRoleDropdown(self, nationID, vclass, typeID):
        Waiting.show('updating')
        modulesAll = self.itemsCache.items.getVehicles(self.__getRoleCriteria(nationID, vclass, typeID)).values()
        roles = []
        data = [{'id': None,
          'label': DIALOGS.RECRUITWINDOW_MENUEMPTYROW}]
        modulesAll.sort()
        skillsConfig = getSkillsConfig()
        for module in modulesAll:
            for role in module.descriptor.type.crewRoles:
                if role[0] in roles:
                    continue
                roles.append(role[0])
                data.append({'id': role[0],
                 'label': convert(skillsConfig.getSkill(role[0]).userString)})

        self.flashObject.as_setRoleDropdown(data)
        Waiting.hide('updating')
        return

    def onWindowClose(self):
        self.destroy()

    @async
    @process
    def __buyTankman(self, nationID, vehTypeID, role, studyType, callback):
        recruiter = TankmanRecruit(int(nationID), int(vehTypeID), role, int(studyType))
        success, msg, msgType, _, _, tmanInvID = yield recruiter.request()
        tankman = None
        if msg:
            SystemMessages.pushI18nMessage(msg, type=msgType)
        if success:
            tankman = self.itemsCache.items.getTankman(tmanInvID)
        callback(tankman)
        return

    @async
    @process
    def __equipTankman(self, tankman, vehicle, slot, callback):
        result = yield TankmanEquip(tankman, vehicle, slot).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
        callback(result.success)

    @async
    @process
    def __buyAndEquipTankman(self, vehicle, slot, studyType, callback):
        result = yield TankmanRecruitAndEquip(vehicle, slot, studyType).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
        callback(result.success)

    @decorators.process('recruting')
    def buyTankman(self, nationID, vehTypeID, role, studyType, slot):
        studyTypeIdx = int(studyType)
        studyGoldCost = self.itemsCache.items.shop.tankmanCost[studyTypeIdx][Currency.GOLD] or 0
        currentMoney = self.itemsCache.items.stats.money
        if currentMoney.gold < studyGoldCost:
            showBuyGoldForCrew(studyGoldCost)
            return
        else:
            if slot is not None and slot != -1:
                vehicle = self.itemsCache.items.getVehicle(self._currentVehicleInvId)
                yield self.__buyAndEquipTankman(vehicle, int(slot), studyTypeIdx)
            else:
                yield self.__buyTankman(int(nationID), int(vehTypeID), role, studyTypeIdx)
            self.onWindowClose()
            return
