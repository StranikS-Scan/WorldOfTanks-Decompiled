# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/PersonalCase.py
import cPickle as pickle
import constants
from adisp import async
from CurrentVehicle import g_currentVehicle
from debug_utils import LOG_ERROR
from gui.shared.tooltips import ACTION_TOOLTIPS_TYPE, ACTION_TOOLTIPS_STATE
from helpers import i18n, strcmp
from gui.Scaleform.framework import AppRef
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.prb_helpers import GlobalListener
from gui.shared.ItemsCache import CACHE_SYNC_REASON
from items import tankmen
from gui import TANKMEN_ROLES_ORDER_DICT, SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.daapi.view.meta.PersonalCaseMeta import PersonalCaseMeta
from gui.shared.events import ShowWindowEvent
from gui.shared.utils import decorators, isVehicleObserver
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Tankman import TankmanSkill
from gui.shared.gui_items.dossier import dumpDossier
from gui.shared.gui_items.serializers import packTankman, packVehicle
from gui.shared.gui_items.processors.tankman import TankmanDismiss, TankmanUnload, TankmanRetraining, TankmanAddSkill, TankmanChangePassport
from gui.shared import EVENT_BUS_SCOPE, events, g_itemsCache, REQ_CRITERIA

class PersonalCase(View, AbstractWindowView, PersonalCaseMeta, GlobalListener, AppRef):

    def __init__(self, ctx):
        super(PersonalCase, self).__init__()
        self.tmanInvID = ctx.get('tankmanID')
        self.tabIndex = ctx.get('page', -1)
        self.dataProvider = PersonalCaseDataProvider(self.tmanInvID)

    def onClientChanged(self, diff):
        inventory = diff.get('inventory', {})
        stats = diff.get('stats', {})
        cache = diff.get('cache', {})
        isTankmanChanged = False
        isTankmanVehicleChanged = False
        if GUI_ITEM_TYPE.TANKMAN in inventory:
            isTankmanChanged = True
            tankmanData = inventory[GUI_ITEM_TYPE.TANKMAN].get('compDescr')
            if tankmanData is not None and self.tmanInvID in tankmanData:
                if tankmanData[self.tmanInvID] is None:
                    return self.destroy()
        isMoneyChanged = 'credits' in stats or 'gold' in stats or 'mayConsumeWalletResources' in cache
        isVehicleChanged = 'unlocks' in stats or 'vehsLock' in cache or GUI_ITEM_TYPE.VEHICLE in inventory
        if isVehicleChanged:
            tankman = g_itemsCache.items.getTankman(self.tmanInvID)
            if tankman.isInTank:
                vehicle = g_itemsCache.items.getVehicle(tankman.vehicleInvID)
                if vehicle.isLocked:
                    return self.destroy()
                vehsDiff = inventory.get(GUI_ITEM_TYPE.VEHICLE, {})
                isTankmanVehicleChanged = len(filter(lambda hive: vehicle.inventoryID in hive or (vehicle.inventoryID, '_r') in hive, vehsDiff.itervalues())) > 0
        if isTankmanChanged or isTankmanVehicleChanged:
            self.__setCommonData()
            self.__setSkillsData()
            self.__setDossierData()
        if isTankmanChanged or isMoneyChanged or isVehicleChanged:
            self.__setRetrainingData()
        if isTankmanChanged or isMoneyChanged:
            self.__setDocumentsData()
        return

    def _refreshData(self, reason, diff):
        if reason != CACHE_SYNC_REASON.SHOP_RESYNC:
            return
        self.__setCommonData()
        self.__setSkillsData()
        self.__setDossierData()
        self.__setRetrainingData()
        self.__setDocumentsData()

    def onPrbFunctionalFinished(self):
        self.__setCommonData()

    def onPlayerStateChanged(self, functional, roster, accountInfo):
        if accountInfo.isCurrentPlayer():
            self.__setCommonData()

    def onUnitFunctionalFinished(self):
        self.__setCommonData()

    def onUnitPlayerStateChanged(self, pInfo):
        if pInfo.isCurrentPlayer():
            self.__setCommonData()

    def onWindowClose(self):
        self.destroy()

    def getCommonData(self):
        self.__setCommonData()

    def getDossierData(self):
        self.__setDossierData()

    def getRetrainingData(self):
        self.__setRetrainingData()

    def getSkillsData(self):
        self.__setSkillsData()

    def getDocumentsData(self):
        self.__setDocumentsData()

    @decorators.process('updating')
    def dismissTankman(self, tmanInvID):
        tankman = g_itemsCache.items.getTankman(int(tmanInvID))
        proc = TankmanDismiss(tankman)
        result = yield proc.request()
        if len(result.userMsg):
            SystemMessages.g_instance.pushMessage(result.userMsg, type=result.sysMsgType)

    @decorators.process('retraining')
    def retrainingTankman(self, inventoryID, innationID, tankmanCostTypeIdx):
        tankman = g_itemsCache.items.getTankman(int(inventoryID))
        vehicleToRecpec = g_itemsCache.items.getItem(GUI_ITEM_TYPE.VEHICLE, tankman.nationID, int(innationID))
        proc = TankmanRetraining(tankman, vehicleToRecpec, tankmanCostTypeIdx)
        result = yield proc.request()
        if len(result.userMsg):
            SystemMessages.g_instance.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    @decorators.process('unloading')
    def unloadTankman(self, tmanInvID, currentVehicleID):
        tankman = g_itemsCache.items.getTankman(int(tmanInvID))
        tmanVehicle = g_itemsCache.items.getVehicle(int(tankman.vehicleInvID))
        if tmanVehicle is None:
            LOG_ERROR("Target tankman's vehicle is not found in inventory", tankman, tankman.vehicleInvID)
            return
        else:
            unloader = TankmanUnload(tmanVehicle, tankman.vehicleSlotIdx)
            result = yield unloader.request()
            if len(result.userMsg):
                SystemMessages.g_instance.pushI18nMessage(result.userMsg, type=result.sysMsgType)
            return

    @decorators.process('updating')
    def changeTankmanPassport(self, invengoryID, firstNameID, lastNameID, iconID):
        tankman = g_itemsCache.items.getTankman(int(invengoryID))
        processor = TankmanChangePassport(tankman, firstNameID, lastNameID, iconID)
        result = yield processor.request()
        if len(result.userMsg):
            SystemMessages.g_instance.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    @decorators.process('studying')
    def addTankmanSkill(self, invengoryID, skillName):
        tankman = g_itemsCache.items.getTankman(int(invengoryID))
        processor = TankmanAddSkill(tankman, skillName)
        result = yield processor.request()
        if len(result.userMsg):
            SystemMessages.g_instance.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    def openExchangeFreeToTankmanXpWindow(self):
        self.fireEvent(events.ShowWindowEvent(events.ShowWindowEvent.SHOW_EXCHANGE_FREE_TO_TANKMAN_XP_WINDOW, {'tankManId': self.tmanInvID}), EVENT_BUS_SCOPE.LOBBY)

    def dropSkills(self):
        self.fireEvent(ShowWindowEvent(ShowWindowEvent.SHOW_TANKMAN_DROP_SKILLS_WINDOW, {'tankmanID': self.tmanInvID}))

    def _populate(self):
        super(PersonalCase, self)._populate()
        g_clientUpdateManager.addCallbacks({'': self.onClientChanged})
        g_itemsCache.onSyncCompleted += self._refreshData
        self.startGlobalListening()

    def _dispose(self):
        self.stopGlobalListening()
        g_itemsCache.onSyncCompleted -= self._refreshData
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(PersonalCase, self)._dispose()

    @decorators.process('updating')
    def __setCommonData(self):
        data = yield self.dataProvider.getCommonData()
        data.update({'tabIndex': self.tabIndex})
        self.as_setCommonDataS(data)

    @decorators.process('updating')
    def __setDossierData(self):
        data = yield self.dataProvider.getDossierData()
        self.as_setDossierDataS(data)

    @decorators.process('updating')
    def __setRetrainingData(self):
        data = yield self.dataProvider.getRetrainingData()
        self.as_setRetrainingDataS(data)

    @decorators.process('updating')
    def __setDocumentsData(self):
        data = yield self.dataProvider.getDocumentsData()
        self.as_setDocumentsDataS(data)

    @decorators.process('updating')
    def __setSkillsData(self):
        data = yield self.dataProvider.getSkillsData()
        self.as_setSkillsDataS(data)


class PersonalCaseDataProvider(object):

    def __init__(self, tmanInvID):
        """
        @param tmanInvID: tankman inventory id
        """
        self.tmanInvID = tmanInvID

    @async
    def getCommonData(self, callback):
        """
        Returns common personal case data for tankman, tankman's vehicles,
        message, flags and so on.
        """
        tankman = g_itemsCache.items.getTankman(self.tmanInvID)
        nativeVehicle = g_itemsCache.items.getItemByCD(tankman.vehicleNativeDescr.type.compactDescr)
        currentVehicle = None
        if tankman.isInTank:
            currentVehicle = g_itemsCache.items.getItemByCD(tankman.vehicleDescr.type.compactDescr)
        isLocked, reason = self.__getTankmanLockMessage(currentVehicle)
        bonuses = tankman.realRoleLevel[1]
        modifiers = []
        if bonuses[0]:
            modifiers.append({'id': 'fromCommander',
             'val': bonuses[0]})
        if bonuses[1]:
            modifiers.append({'id': 'fromSkills',
             'val': bonuses[1]})
        if bonuses[2] or bonuses[3]:
            modifiers.append({'id': 'fromEquipment',
             'val': bonuses[2] + bonuses[3]})
        if bonuses[4]:
            modifiers.append({'id': 'penalty',
             'val': bonuses[4]})
        callback({'tankman': packTankman(tankman),
         'currentVehicle': packVehicle(currentVehicle) if currentVehicle is not None else None,
         'nativeVehicle': packVehicle(nativeVehicle),
         'isOpsLocked': isLocked or g_currentVehicle.isLocked(),
         'lockMessage': reason,
         'modifiers': modifiers})
        return

    @async
    def getDossierData(self, callback):
        """
        Returns dict of dossier data: information stats blocks and
        achievements list.
        """
        tmanDossier = g_itemsCache.items.getTankmanDossier(self.tmanInvID)
        if tmanDossier is None:
            callback(None)
            return
        else:
            achieves = tmanDossier.getTotalStats().getAchievements(isInDossier=True)
            pickledDossierCompDescr = dumpDossier(tmanDossier)
            packedAchieves = []
            for sectionIdx, section in enumerate(achieves):
                packedAchieves.append([])
                for achievement in section:
                    packedAchieves[sectionIdx].append(self.__packAchievement(achievement, pickledDossierCompDescr))

            callback({'achievements': packedAchieves,
             'stats': tmanDossier.getStats()})
            return

    @async
    def getRetrainingData(self, callback):
        items = g_itemsCache.items
        tankman = items.getTankman(self.tmanInvID)
        criteria = REQ_CRITERIA.NATIONS([tankman.nationID]) | REQ_CRITERIA.UNLOCKED
        vData = items.getVehicles(criteria)
        tDescr = tankman.descriptor
        vehiclesData = sorted(vData.values())
        result = []
        for vehicle in vehiclesData:
            vDescr = vehicle.descriptor
            if isVehicleObserver(vDescr.type.compactDescr):
                continue
            for role in vDescr.type.crewRoles:
                if tDescr.role == role[0]:
                    result.append({'innationID': vehicle.innationID,
                     'vehicleType': vehicle.type,
                     'userName': vehicle.shortUserName})
                    break

        shopPrices, action = items.shop.getTankmanCostWithDefaults()
        callback({'money': (items.stats.credits, items.stats.gold),
         'tankmanCost': shopPrices,
         'action': action,
         'vehicles': result})

    @async
    def getSkillsData(self, callback):
        tankman = g_itemsCache.items.getTankman(self.tmanInvID)
        tankmanDescr = tankman.descriptor
        result = []
        commonSkills = []
        for skill in tankmen.COMMON_SKILLS:
            if skill not in tankmanDescr.skills:
                commonSkills.append(self.__packSkill(tankman, TankmanSkill(skill)))

        result.append({'id': 'common',
         'skills': commonSkills})
        for role in TANKMEN_ROLES_ORDER_DICT['plain']:
            roleSkills = tankmen.SKILLS_BY_ROLES.get(role, tuple())
            if role not in tankman.combinedRoles:
                continue
            skills = []
            for skill in roleSkills:
                if skill not in tankmen.COMMON_SKILLS and skill not in tankmanDescr.skills:
                    skills.append(self.__packSkill(tankman, TankmanSkill(skill)))

            result.append({'id': role,
             'skills': skills})

        callback(result)

    @async
    def getDocumentsData(self, callback):
        items = g_itemsCache.items
        config = tankmen.getNationConfig(items.getTankman(self.tmanInvID).nationID)
        shopPrice = items.shop.passportChangeCost
        defaultPrice = items.shop.defaults.passportChangeCost
        action = None
        if shopPrice != defaultPrice:
            action = {'type': ACTION_TOOLTIPS_TYPE.ECONOMICS,
             'key': 'passportChangeCost',
             'isBuying': True,
             'state': (0, ACTION_TOOLTIPS_STATE.DISCOUNT),
             'newPrice': (0, shopPrice),
             'oldPrice': (0, defaultPrice)}
        callback({'money': (items.stats.credits, items.stats.gold),
         'passportChangeCost': shopPrice,
         'action': action,
         'firstnames': self.__getDocNormalGroupValues(config, 'firstNames'),
         'lastnames': self.__getDocNormalGroupValues(config, 'lastNames'),
         'icons': self.__getDocNormalGroupValues(config, 'icons')})
        return

    @staticmethod
    def __getDocNormalGroupValues(config, groupName):
        result = []
        for group in config['normalGroups']:
            for idx in group['%sList' % groupName]:
                result.append({'id': idx,
                 'value': config[groupName][idx]})

        if groupName != 'icons':
            result = sorted(result, key=lambda sortField: sortField['value'], cmp=lambda a, b: strcmp(unicode(a), unicode(b)))
        return result

    @staticmethod
    def __packSkill(tankman, skillItem):
        return {'id': skillItem.name,
         'name': skillItem.userName,
         'desc': skillItem.shortDescription,
         'enabled': True,
         'tankmanID': tankman.invID,
         'tooltip': None}

    @staticmethod
    def __getTankmanLockMessage(vehicle):
        if vehicle is None:
            return (False, '')
        elif vehicle.isInBattle:
            return (False, i18n.makeString('#menu:tankmen/lockReason/inbattle'))
        elif vehicle.isBroken:
            return (False, i18n.makeString('#menu:tankmen/lockReason/broken'))
        else:
            if g_currentVehicle.item == vehicle:
                dispatcher = g_prbLoader.getDispatcher()
                if dispatcher is not None:
                    permission = dispatcher.getGUIPermissions()
                    if not permission.canChangeVehicle():
                        return (True, i18n.makeString('#menu:tankmen/lockReason/prebattle'))
            return (False, '')

    @staticmethod
    def __packAchievement(achieve, dossierCompDescr):
        icons = achieve.getIcons()
        return {'name': achieve.getName(),
         'block': achieve.getBlock(),
         'userName': achieve.getUserName(),
         'description': achieve.getUserDescription(),
         'type': achieve.getType(),
         'section': achieve.getSection(),
         'value': achieve.getValue(),
         'localizedValue': achieve.getI18nValue(),
         'levelUpValue': achieve.getLevelUpValue(),
         'isDone': achieve.isDone(),
         'isInDossier': achieve.isInDossier(),
         'icon': {'big': icons['180x180'],
                  'small': icons['67x71']},
         'dossierType': constants.DOSSIER_TYPE.TANKMAN,
         'dossierCompDescr': dossierCompDescr}
