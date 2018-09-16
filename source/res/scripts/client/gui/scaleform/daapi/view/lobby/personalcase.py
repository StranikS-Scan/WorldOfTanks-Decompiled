# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/PersonalCase.py
import operator
import constants
from CurrentVehicle import g_currentVehicle
from account_helpers.settings_core.settings_constants import TUTORIAL
from adisp import async
from debug_utils import LOG_ERROR
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.AchievementsUtils import AchievementsUtils
from gui.Scaleform.daapi.view.lobby.store.browser.ingameshop_helpers import isIngameShopEnabled
from gui.Scaleform.daapi.view.meta.PersonalCaseMeta import PersonalCaseMeta
from gui.Scaleform.locale.MENU import MENU
from gui.ingame_shop import showBuyGoldForCrew
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared import EVENT_BUS_SCOPE, events
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.events import LoadViewEvent
from gui.shared.formatters import text_styles
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.dossier import dumpDossier
from gui.shared.gui_items.processors.tankman import TankmanDismiss, TankmanUnload, TankmanRetraining, TankmanAddSkill, TankmanChangePassport
from gui.shared.gui_items.serializers import packTankman, packVehicle, packTraining
from gui.shared.money import Money
from gui.shared.tooltips import ACTION_TOOLTIPS_TYPE
from gui.shared.tooltips.formatters import packActionTooltipData
from gui.shared.utils import decorators, roundByModulo
from gui.shared.utils.functions import getViewName, makeTooltip
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from helpers import i18n, strcmp
from items import tankmen
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS

class PersonalCase(PersonalCaseMeta, IGlobalListener):
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, ctx=None):
        super(PersonalCase, self).__init__()
        self.tmanInvID = ctx.get('tankmanID')
        self.tabIndex = ctx.get('page', -1)
        self.dataProvider = PersonalCaseDataProvider(self.tmanInvID)
        tankman = self.itemsCache.items.getTankman(self.tmanInvID)
        self.vehicle = self.itemsCache.items.getItemByCD(tankman.vehicleNativeDescr.type.compactDescr)

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
        isVehsLockExist = 'vehsLock' in cache
        isMoneyChanged = 'credits' in stats or 'gold' in stats or 'mayConsumeWalletResources' in cache
        isVehicleChanged = 'unlocks' in stats or isVehsLockExist or GUI_ITEM_TYPE.VEHICLE in inventory
        isFreeXpChanged = 'freeXP' in stats
        if isVehicleChanged:
            tankman = self.itemsCache.items.getTankman(self.tmanInvID)
            if tankman.isInTank:
                vehicle = self.itemsCache.items.getVehicle(tankman.vehicleInvID)
                if vehicle.isLocked:
                    return self.destroy()
                vehsDiff = inventory.get(GUI_ITEM_TYPE.VEHICLE, {})
                isTankmanVehicleChanged = any((vehicle.invID in hive or (vehicle.invID, '_r') in hive for hive in vehsDiff.itervalues()))
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

    def onPrbEntitySwitched(self):
        self.__setCommonData()

    def onPlayerStateChanged(self, entity, roster, accountInfo):
        if accountInfo.isCurrentPlayer():
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
        tankman = self.itemsCache.items.getTankman(int(tmanInvID))
        proc = TankmanDismiss(tankman)
        result = yield proc.request()
        if result.userMsg:
            SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)

    @decorators.process('retraining')
    def retrainingTankman(self, inventoryID, tankmanCostTypeIdx):
        operationCost = self.itemsCache.items.shop.tankmanCost[tankmanCostTypeIdx].get('gold', 0)
        currentGold = self.itemsCache.items.stats.gold
        if currentGold < operationCost and isIngameShopEnabled():
            showBuyGoldForCrew(operationCost)
            return
        tankman = self.itemsCache.items.getTankman(int(inventoryID))
        proc = TankmanRetraining(tankman, self.vehicle, tankmanCostTypeIdx)
        result = yield proc.request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    @decorators.process('unloading')
    def unloadTankman(self, tmanInvID, currentVehicleID):
        tankman = self.itemsCache.items.getTankman(int(tmanInvID))
        tmanVehicle = self.itemsCache.items.getVehicle(int(tankman.vehicleInvID))
        if tmanVehicle is None:
            LOG_ERROR("Target tankman's vehicle is not found in inventory", tankman, tankman.vehicleInvID)
            return
        else:
            unloader = TankmanUnload(tmanVehicle, tankman.vehicleSlotIdx)
            result = yield unloader.request()
            if result.userMsg:
                SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
            return

    @decorators.process('updating')
    def changeTankmanPassport(self, inventoryID, firstNameID, firstNameGroup, lastNameID, lastNameGroup, iconID, iconGroup):
        items = self.itemsCache.items
        tankman = items.getTankman(inventoryID)
        if tankman.descriptor.isFemale:
            passportChangeCost = items.shop.passportFemaleChangeCost
        else:
            passportChangeCost = items.shop.passportChangeCost
        currentGold = self.itemsCache.items.stats.gold
        if currentGold < passportChangeCost and isIngameShopEnabled():
            showBuyGoldForCrew(passportChangeCost)
            return

        def checkFlashInt(value):
            return None if value == -1 else value

        firstNameID = checkFlashInt(firstNameID)
        lastNameID = checkFlashInt(lastNameID)
        iconID = checkFlashInt(iconID)
        tankman = self.itemsCache.items.getTankman(int(inventoryID))
        result = yield TankmanChangePassport(tankman, firstNameID, firstNameGroup, lastNameID, lastNameGroup, iconID, iconGroup).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    @decorators.process('studying')
    def addTankmanSkill(self, invengoryID, skillName):
        tankman = self.itemsCache.items.getTankman(int(invengoryID))
        processor = TankmanAddSkill(tankman, skillName)
        result = yield processor.request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    def openExchangeFreeToTankmanXpWindow(self):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.EXCHANGE_FREE_TO_TANKMAN_XP_WINDOW, getViewName(VIEW_ALIAS.EXCHANGE_FREE_TO_TANKMAN_XP_WINDOW, self.tmanInvID), {'tankManId': self.tmanInvID}), EVENT_BUS_SCOPE.LOBBY)

    def changeRetrainVehicle(self, intCD):
        self.vehicle = self.itemsCache.items.getItemByCD(intCD)
        self.__setRetrainingData()

    def dropSkills(self):
        self.fireEvent(LoadViewEvent(VIEW_ALIAS.TANKMAN_SKILLS_DROP_WINDOW, getViewName(VIEW_ALIAS.TANKMAN_SKILLS_DROP_WINDOW, self.tmanInvID), {'tankmanID': self.tmanInvID}), EVENT_BUS_SCOPE.LOBBY)

    def _populate(self):
        super(PersonalCase, self)._populate()
        g_clientUpdateManager.addCallbacks({'': self.onClientChanged})
        self.itemsCache.onSyncCompleted += self._refreshData
        self.startGlobalListening()
        self.setupContextHints(TUTORIAL.PERSONAL_CASE)
        self.addListener(events.FightButtonEvent.FIGHT_BUTTON_UPDATE, self.__updatePrbState, scope=EVENT_BUS_SCOPE.LOBBY)

    def _dispose(self):
        self.stopGlobalListening()
        self.itemsCache.onSyncCompleted -= self._refreshData
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.removeListener(events.FightButtonEvent.FIGHT_BUTTON_UPDATE, self.__updatePrbState, scope=EVENT_BUS_SCOPE.LOBBY)
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
        data = yield self.dataProvider.getRetrainingData(self.vehicle)
        self.as_setRetrainingDataS(data)

    @decorators.process('updating')
    def __setDocumentsData(self):
        data = yield self.dataProvider.getDocumentsData()
        self.as_setDocumentsDataS(data)

    @decorators.process('updating')
    def __setSkillsData(self):
        data = yield self.dataProvider.getSkillsData()
        self.as_setSkillsDataS(data)

    def __updatePrbState(self, *args):
        if not self.prbEntity.getPermissions().canChangeVehicle():
            self.destroy()


STATS_TAB_INDEX = 0
TRAINING_TAB_INDEX = 1
SKILLS_TAB_INDEX = 2
DOCS_TAB_INDEX = 3
PERSONAL_CASE_STATS = 'crewTankmanStats'
PERSONAL_CASE_RETRAINING = 'CrewTankmanRetraining'
PERSONAL_CASE_SKILLS = 'PersonalCaseSkills'
PERSONAL_CASE_DOCS = 'PersonalCaseDocs'

class PersonalCaseDataProvider(object):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, tmanInvID):
        self.tmanInvID = tmanInvID

    @async
    def getCommonData(self, callback):
        items = self.itemsCache.items
        tankman = items.getTankman(self.tmanInvID)
        changeRoleCost = items.shop.changeRoleCost
        defaultChangeRoleCost = items.shop.defaults.changeRoleCost
        if changeRoleCost != defaultChangeRoleCost:
            discount = packActionTooltipData(ACTION_TOOLTIPS_TYPE.ECONOMICS, 'changeRoleCost', True, Money(gold=changeRoleCost), Money(gold=defaultChangeRoleCost))
        else:
            discount = None
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
        td = tankman.descriptor
        changeRoleEnabled = tankmen.tankmenGroupCanChangeRole(td.nationID, td.gid, td.isPremium)
        if changeRoleEnabled:
            tooltipChangeRole = makeTooltip(TOOLTIPS.CREW_ROLECHANGE_HEADER, TOOLTIPS.CREW_ROLECHANGE_TEXT)
        else:
            tooltipChangeRole = makeTooltip(TOOLTIPS.CREW_ROLECHANGEFORBID_HEADER, TOOLTIPS.CREW_ROLECHANGEFORBID_TEXT)
        showDocumentTab = not td.getRestrictions().isPassportReplacementForbidden()
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
         'isOpsLocked': isLocked,
         'lockMessage': reason,
         'modifiers': modifiers,
         'enoughFreeXPForTeaching': enoughFreeXPForTeaching,
         'tabsData': self.getTabsButtons(showDocumentTab),
         'tooltipDismiss': TOOLTIPS.BARRACKS_TANKMEN_DISMISS,
         'tooltipUnload': TOOLTIPS.BARRACKS_TANKMEN_UNLOAD,
         'dismissEnabled': True,
         'unloadEnabled': True,
         'changeRoleEnabled': changeRoleEnabled,
         'tooltipChangeRole': tooltipChangeRole,
         'actionChangeRole': discount})
        return

    def getTabsButtons(self, showDocumentTab):
        tabs = [{'index': STATS_TAB_INDEX,
          'label': MENU.TANKMANPERSONALCASE_TABBATTLEINFO,
          'linkage': PERSONAL_CASE_STATS}, {'index': TRAINING_TAB_INDEX,
          'label': MENU.TANKMANPERSONALCASE_TABTRAINING,
          'linkage': PERSONAL_CASE_RETRAINING}, {'index': SKILLS_TAB_INDEX,
          'label': MENU.TANKMANPERSONALCASE_TABSKILLS,
          'linkage': PERSONAL_CASE_SKILLS}]
        if showDocumentTab:
            tabs.append({'index': DOCS_TAB_INDEX,
             'label': MENU.TANKMANPERSONALCASE_TABDOCS,
             'linkage': PERSONAL_CASE_DOCS})
        return tabs

    @async
    def getDossierData(self, callback):
        tmanDossier = self.itemsCache.items.getTankmanDossier(self.tmanInvID)
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
             'stats': tmanDossier.getStats(self.itemsCache.items.getTankman(self.tmanInvID)),
             'firstMsg': self.__makeStandardText(MENU.CONTEXTMENU_PERSONALCASE_STATS_FIRSTINFO),
             'secondMsg': self.__makeStandardText(MENU.CONTEXTMENU_PERSONALCASE_STATS_SECONDINFO)})
            return

    def __makeStandardText(self, locale):
        return text_styles.standard(i18n.makeString(locale))

    @async
    def getRetrainingData(self, targetVehicle, callback):
        items = self.itemsCache.items
        tankman = items.getTankman(self.tmanInvID)
        nativeVehicleCD = tankman.vehicleNativeDescr.type.compactDescr
        criteria = REQ_CRITERIA.NATIONS([tankman.nationID]) | REQ_CRITERIA.UNLOCKED | ~REQ_CRITERIA.VEHICLE.OBSERVER
        if not constants.IS_IGR_ENABLED:
            criteria |= ~REQ_CRITERIA.VEHICLE.IS_PREMIUM_IGR
        if constants.IS_DEVELOPMENT:
            criteria |= ~REQ_CRITERIA.VEHICLE.IS_BOT
        vData = items.getVehicles(criteria)
        tDescr = tankman.descriptor
        vehiclesData = vData.values()
        if nativeVehicleCD not in vData:
            vehiclesData.append(items.getItemByCD(nativeVehicleCD))
        result = []
        for vehicle in sorted(vehiclesData):
            vDescr = vehicle.descriptor
            for role in vDescr.type.crewRoles:
                if tDescr.role == role[0]:
                    result.append({'intCD': vehicle.intCD,
                     'vehicleType': vehicle.type,
                     'userName': vehicle.shortUserName})
                    break

        callback({'vehicles': result,
         'retrainButtonsData': packTraining(targetVehicle, [tankman])})

    @async
    def getSkillsData(self, callback):
        tankman = self.itemsCache.items.getTankman(self.tmanInvID)
        callback(tankman.getSkillsToLearn())

    @async
    def getDocumentsData(self, callback):
        items = self.itemsCache.items
        tankman = items.getTankman(self.tmanInvID)
        config = tankmen.getNationConfig(tankman.nationID)
        if tankman.descriptor.isFemale:
            shopPrice = items.shop.passportFemaleChangeCost
            defaultPrice = items.shop.defaults.passportFemaleChangeCost
        else:
            shopPrice = items.shop.passportChangeCost
            defaultPrice = items.shop.defaults.passportChangeCost
        currentGold = self.itemsCache.items.stats.gold
        enableSubmitButton = shopPrice <= currentGold or isIngameShopEnabled()
        action = None
        if shopPrice != defaultPrice:
            action = packActionTooltipData(ACTION_TOOLTIPS_TYPE.ECONOMICS, 'passportChangeCost', True, Money(gold=shopPrice), Money(gold=defaultPrice))
        callback({'money': items.stats.money.toMoneyTuple(),
         'passportChangeCost': shopPrice,
         'action': action,
         'firstnames': self.__getDocGroupValues(tankman, config, operator.attrgetter('firstNamesList'), config.getFirstName),
         'lastnames': self.__getDocGroupValues(tankman, config, operator.attrgetter('lastNamesList'), config.getLastName),
         'icons': self.__getDocGroupValues(tankman, config, operator.attrgetter('iconsList'), config.getIcon, sortNeeded=False),
         'enableSubmitButton': enableSubmitButton})
        return

    @staticmethod
    def __getDocGroupValues(tankman, config, listGetter, valueGetter, sortNeeded=True):
        result = []
        isPremium, isFemale = tankman.descriptor.isPremium, tankman.descriptor.isFemale
        for gIdx, group in enumerate(config.getGroups(isPremium)):
            if not group.notInShop and group.isFemales == isFemale:
                for idx in listGetter(group):
                    result.append({'id': idx,
                     'group': gIdx,
                     'value': valueGetter(idx)})

        if sortNeeded:
            result = sorted(result, key=lambda sortField: sortField['value'], cmp=lambda a, b: strcmp(unicode(a), unicode(b)))
        return result

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
