# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/recruitWindow/RecruitWindow.py
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.shared.tooltips import ACTION_TOOLTIPS_TYPE, ACTION_TOOLTIPS_STATE
import nations
from gui.Scaleform.locale.DIALOGS import DIALOGS
from gui.Scaleform.locale.MENU import MENU
from adisp import process, async
from items.tankmen import getSkillsConfig
from helpers.i18n import convert
from gui import GUI_NATIONS, SystemMessages
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.view.meta.RecruitWindowMeta import RecruitWindowMeta
from gui.Scaleform.framework.entities.View import View
from gui.shared import g_itemsCache, REQ_CRITERIA
from gui.shared.utils import decorators
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.processors.tankman import TankmanRecruit, TankmanEquip, TankmanRecruitAndEquip

class RecruitWindow(RecruitWindowMeta):

    def __init__(self, ctx = None):
        super(RecruitWindow, self).__init__()
        self._initData = ctx.get('data', None)
        self._menuEnabled = ctx.get('menuEnabled', False)
        self._currentVehicleInvId = ctx.get('currentVehicleId', -1)
        return

    def _populate(self):
        View._populate(self)
        self.__getInitialData()
        if self._currentVehicleInvId != -1:
            g_clientUpdateManager.addCallbacks({'inventory': self.onInventoryChanged})
        g_clientUpdateManager.addCallbacks({'stats.credits': self.onCreditsChange,
         'stats.gold': self.onGoldChange,
         'cache.mayConsumeWalletResources': self.onGoldChange})

    def onGoldChange(self, value):
        if self._currentVehicleInvId is not None:
            self.as_setGoldChangedS(g_itemsCache.items.stats.gold)
        return

    def onCreditsChange(self, value):
        if self._currentVehicleInvId is not None:
            self.as_setCreditsChangedS(value)
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

    def __getInitialData(self):
        credits, gold = g_itemsCache.items.stats.money
        shop = g_itemsCache.items.shop
        upgradeParams = shop.tankmanCost
        defUpgradeParams = shop.defaults.tankmanCost
        schoolUpgradePrice = round(upgradeParams[1]['credits'])
        schoolUpgradeDefPrice = round(defUpgradeParams[1]['credits'])
        schoolUpgradeAction = None
        if schoolUpgradePrice != schoolUpgradeDefPrice:
            schoolUpgradeAction = {'type': ACTION_TOOLTIPS_TYPE.ECONOMICS,
             'key': 'creditsTankmanCost',
             'isBuying': True,
             'state': (ACTION_TOOLTIPS_STATE.DISCOUNT, None),
             'newPrice': (schoolUpgradePrice, 0),
             'oldPrice': (schoolUpgradeDefPrice, 0)}
        academyUpgradePrice = round(upgradeParams[2]['gold'])
        academyUpgradeDefPrice = round(defUpgradeParams[2]['gold'])
        academyUpgradeAction = None
        if academyUpgradePrice != academyUpgradeDefPrice:
            academyUpgradeAction = {'type': ACTION_TOOLTIPS_TYPE.ECONOMICS,
             'key': 'goldTankmanCost',
             'isBuying': True,
             'state': (None, ACTION_TOOLTIPS_STATE.DISCOUNT),
             'newPrice': (0, academyUpgradePrice),
             'oldPrice': (0, academyUpgradeDefPrice)}
        data = {'credits': credits,
         'gold': gold,
         'schoolUpgradePrice': schoolUpgradePrice,
         'schoolUpgradeActionPriceData': schoolUpgradeAction,
         'academyUpgradePrice': academyUpgradePrice,
         'academyUpgradeActionPriceData': academyUpgradeAction,
         'data': self._initData,
         'menuEnabled': self._menuEnabled}
        self.flashObject.as_initData(data)
        return

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
        modulesAll = g_itemsCache.items.getVehicles(self.__getRoleCriteria(nationID, tankType, typeID)).values()
        modulesAll.sort()
        for module in modulesAll:
            typesDP.append({'id': module.innationID,
             'label': module.shortUserName})
            for role in module.descriptor.type.crewRoles:
                if role[0] == roleType:
                    rolesDP.append({'id': role[0],
                     'label': convert(getSkillsConfig()[role[0]]['userString'])})

            break

        self.flashObject.as_setAllDropdowns(nationsDP, classesDP, typesDP, rolesDP)
        return

    def __getNationsCriteria(self):
        return REQ_CRITERIA.UNLOCKED | ~REQ_CRITERIA.VEHICLE.OBSERVER

    def updateNationDropdown(self):
        vehsItems = g_itemsCache.items.getVehicles(self.__getNationsCriteria())
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
        return self.__getNationsCriteria() | REQ_CRITERIA.NATIONS([nationID])

    def updateVehicleClassDropdown(self, nationID):
        Waiting.show('updating')
        modulesAll = g_itemsCache.items.getVehicles(self.__getClassesCriteria(nationID)).values()
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
        return self.__getClassesCriteria(nationID) | REQ_CRITERIA.VEHICLE.CLASSES([vclass])

    def updateVehicleTypeDropdown(self, nationID, vclass):
        Waiting.show('updating')
        modulesAll = g_itemsCache.items.getVehicles(self.__getVehicleTypeCriteria(nationID, vclass)).values()
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
        modulesAll = g_itemsCache.items.getVehicles(self.__getRoleCriteria(nationID, vclass, typeID)).values()
        roles = []
        data = [{'id': None,
          'label': DIALOGS.RECRUITWINDOW_MENUEMPTYROW}]
        modulesAll.sort()
        for module in modulesAll:
            for role in module.descriptor.type.crewRoles:
                if role[0] in roles:
                    continue
                roles.append(role[0])
                data.append({'id': role[0],
                 'label': convert(getSkillsConfig()[role[0]]['userString'])})

        self.flashObject.as_setRoleDropdown(data)
        Waiting.hide('updating')
        return

    def onWindowClose(self):
        self.destroy()

    @async
    @process
    def __buyTankman(self, nationID, vehTypeID, role, studyType, callback):
        recruiter = TankmanRecruit(int(nationID), int(vehTypeID), role, int(studyType))
        success, msg, msgType, tmanInvID = yield recruiter.request()
        tankman = None
        if len(msg):
            SystemMessages.pushI18nMessage(msg, type=msgType)
        if success:
            tankman = g_itemsCache.items.getTankman(tmanInvID)
        callback(tankman)
        return

    @async
    @process
    def __equipTankman(self, tankman, vehicle, slot, callback):
        result = yield TankmanEquip(tankman, vehicle, slot).request()
        if len(result.userMsg):
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
        callback(result.success)

    @async
    @process
    def __buyAndEquipTankman(self, vehicle, slot, studyType, callback):
        result = yield TankmanRecruitAndEquip(vehicle, slot, studyType).request()
        if len(result.userMsg):
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
        callback(result.success)

    @decorators.process('recruting')
    def buyTankman(self, nationID, vehTypeID, role, studyType, slot):
        if slot is not None and slot != -1:
            vehicle = g_itemsCache.items.getVehicle(self._currentVehicleInvId)
            yield self.__buyAndEquipTankman(vehicle, int(slot), int(studyType))
        else:
            yield self.__buyTankman(int(nationID), int(vehTypeID), role, int(studyType))
        self.onWindowClose()
        return
