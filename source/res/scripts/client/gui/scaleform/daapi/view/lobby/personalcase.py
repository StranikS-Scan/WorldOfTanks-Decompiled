# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/PersonalCase.py
import constants
from adisp import async
from CurrentVehicle import g_currentVehicle
from gui.Scaleform.daapi.view.AchievementsUtils import AchievementsUtils
from debug_utils import LOG_ERROR
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.shared.formatters import text_styles
from gui.shared.tooltips import ACTION_TOOLTIPS_TYPE, ACTION_TOOLTIPS_STATE
from gui.shared.utils.functions import getViewName
from helpers import i18n, strcmp
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.prb_helpers import GlobalListener
from gui.shared.ItemsCache import CACHE_SYNC_REASON
from items import tankmen
from gui import TANKMEN_ROLES_ORDER_DICT, SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.meta.PersonalCaseMeta import PersonalCaseMeta
from gui.shared.events import LoadViewEvent
from gui.shared.utils import decorators, isVehicleObserver, roundByModulo
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Tankman import TankmanSkill
from gui.shared.gui_items.dossier import dumpDossier
from gui.shared.gui_items.serializers import packTankman, packVehicle
from gui.shared.gui_items.processors.tankman import TankmanDismiss, TankmanUnload, TankmanRetraining, TankmanAddSkill, TankmanChangePassport
from gui.shared import EVENT_BUS_SCOPE, events, g_itemsCache, REQ_CRITERIA
from account_helpers.settings_core.settings_constants import TUTORIAL

class PersonalCase(PersonalCaseMeta, GlobalListener):

    def __init__(self, ctx = None):
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
            tankmanData = inventory[GUI_ITEM_TYPE.TANKMAN].get('compDescr')
            if tankmanData is not None and self.tmanInvID in tankmanData:
                isTankmanChanged = True
                if tankmanData[self.tmanInvID] is None:
                    return self.destroy()
            if self.tmanInvID in inventory[GUI_ITEM_TYPE.TANKMAN].get('vehicle', {}):
                isTankmanChanged = True
        isMoneyChanged = 'credits' in stats or 'gold' in stats or 'mayConsumeWalletResources' in cache
        isVehicleChanged = 'unlocks' in stats or 'vehsLock' in cache or GUI_ITEM_TYPE.VEHICLE in inventory
        isFreeXpChanged = 'freeXP' in stats
        if isVehicleChanged:
            tankman = g_itemsCache.items.getTankman(self.tmanInvID)
            if tankman.isInTank:
                vehicle = g_itemsCache.items.getVehicle(tankman.vehicleInvID)
                if vehicle.isLocked:
                    return self.destroy()
                vehsDiff = inventory.get(GUI_ITEM_TYPE.VEHICLE, {})
                isTankmanVehicleChanged = len(filter(lambda hive: vehicle.inventoryID in hive or (vehicle.inventoryID, '_r') in hive, vehsDiff.itervalues())) > 0
        if isTankmanChanged or isTankmanVehicleChanged or isFreeXpChanged:
            self.__setCommonData()
        if isTankmanChanged or isTankmanVehicleChanged:
            self.__setSkillsData()
            self.__setDossierData()
        if isTankmanChanged or isMoneyChanged or isTankmanVehicleChanged:
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

    def openChangeRoleWindow(self):
        ctx = {'tankmanID': self.tmanInvID}
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.ROLE_CHANGE, VIEW_ALIAS.ROLE_CHANGE, ctx=ctx), scope=EVENT_BUS_SCOPE.LOBBY)

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
    def changeTankmanPassport(self, invengoryID, firstNameID, firstNameGroup, lastNameID, lastNameGroup, iconID, iconGroup):

        def checkFlashInt(value):
            if value == -1:
                return None
            else:
                return value

        firstNameID = checkFlashInt(firstNameID)
        lastNameID = checkFlashInt(lastNameID)
        iconID = checkFlashInt(iconID)
        tankman = g_itemsCache.items.getTankman(int(invengoryID))
        result = yield TankmanChangePassport(tankman, firstNameID, firstNameGroup, lastNameID, lastNameGroup, iconID, iconGroup).request()
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
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.EXCHANGE_FREE_TO_TANKMAN_XP_WINDOW, getViewName(VIEW_ALIAS.EXCHANGE_FREE_TO_TANKMAN_XP_WINDOW, self.tmanInvID), {'tankManId': self.tmanInvID}), EVENT_BUS_SCOPE.LOBBY)

    def dropSkills(self):
        self.fireEvent(LoadViewEvent(VIEW_ALIAS.TANKMAN_SKILLS_DROP_WINDOW, getViewName(VIEW_ALIAS.TANKMAN_SKILLS_DROP_WINDOW, self.tmanInvID), {'tankmanID': self.tmanInvID}), EVENT_BUS_SCOPE.LOBBY)

    def _populate(self):
        super(PersonalCase, self)._populate()
        g_clientUpdateManager.addCallbacks({'': self.onClientChanged})
        g_itemsCache.onSyncCompleted += self._refreshData
        self.startGlobalListening()
        self.setupContextHints(TUTORIAL.PERSONAL_CASE)

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
        items = g_itemsCache.items
        tankman = items.getTankman(self.tmanInvID)
        rate = items.shop.freeXPToTManXPRate
        if rate:
            toNextPrcLeft = roundByModulo(tankman.getNextLevelXpCost(), rate)
            enoughFreeXPForTeaching = items.stats.freeXP - max(1, toNextPrcLeft / rate) >= 0
        else:
            enoughFreeXPForTeaching = False
        nativeVehicle = items.getItemByCD(tankman.vehicleNativeDescr.type.compactDescr)
        currentVehicle = None
        if tankman.isInTank:
            currentVehicle = items.getItemByCD(tankman.vehicleDescr.type.compactDescr)
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
         'modifiers': modifiers,
         'enoughFreeXPForTeaching': enoughFreeXPForTeaching})
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
             'stats': tmanDossier.getStats(g_itemsCache.items.getTankman(self.tmanInvID)),
             'firstMsg': self.__makeStandardText(MENU.CONTEXTMENU_PERSONALCASE_STATS_FIRSTINFO),
             'secondMsg': self.__makeStandardText(MENU.CONTEXTMENU_PERSONALCASE_STATS_SECONDINFO)})
            return

    def __makeStandardText(self, locale):
        return text_styles.standard(i18n.makeString(locale))

    @async
    def getRetrainingData(self, callback):
        items = g_itemsCache.items
        tankman = items.getTankman(self.tmanInvID)
        nativeVehicleCD = tankman.vehicleNativeDescr.type.compactDescr
        criteria = REQ_CRITERIA.NATIONS([tankman.nationID]) | REQ_CRITERIA.UNLOCKED
        vData = items.getVehicles(criteria)
        tDescr = tankman.descriptor
        vehiclesData = vData.values()
        if nativeVehicleCD not in vData:
            vehiclesData.append(items.getItemByCD(nativeVehicleCD))
        result = []
        for vehicle in sorted(vehiclesData):
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
        tankman = items.getTankman(self.tmanInvID)
        config = tankmen.getNationConfig(tankman.nationID)
        if tankman.descriptor.isFemale:
            shopPrice = items.shop.passportFemaleChangeCost
            defaultPrice = items.shop.defaults.passportFemaleChangeCost
        else:
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
         'firstnames': self.__getDocGroupValues(tankman, config, 'firstNames'),
         'lastnames': self.__getDocGroupValues(tankman, config, 'lastNames'),
         'icons': self.__getDocGroupValues(tankman, config, 'icons', sortNeeded=False)})
        return

    @staticmethod
    def __getDocGroupValues(tankman, config, subGroupName, sortNeeded = True):
        result = []
        isPremium, isFemale = tankman.descriptor.isPremium, tankman.descriptor.isFemale
        groupName = 'premiumGroups' if isPremium else 'normalGroups'
        for gIdx, group in enumerate(config[groupName]):
            if not group['notInShop'] and group['isFemales'] == isFemale:
                for idx in group['%sList' % subGroupName]:
                    result.append({'id': idx,
                     'group': gIdx,
                     'value': config[subGroupName][idx]})

        if sortNeeded:
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
        commonData = AchievementsUtils.getCommonAchievementData(achieve, constants.DOSSIER_TYPE.TANKMAN, dossierCompDescr)
        commonData['counterType'] = AchievementsUtils.getCounterType(achieve)
        return commonData

    def __roundByModulo(self, targetXp, rate):
        left_rate = targetXp % rate
        if left_rate > 0:
            targetXp += rate - left_rate
        return targetXp
