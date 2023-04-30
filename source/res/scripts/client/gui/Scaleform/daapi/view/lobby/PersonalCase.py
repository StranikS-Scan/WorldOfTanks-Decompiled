# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/PersonalCase.py
import operator
import typing
from account_helpers.AccountSettings import CREW_SKINS_VIEWED, CREW_SKINS_HISTORICAL_VISIBLE
from account_helpers.settings_core.settings_constants import GAME
import SoundGroups
import constants
from CurrentVehicle import g_currentVehicle
from account_helpers import AccountSettings
from adisp import adisp_async
from debug_utils import LOG_ERROR
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.AchievementsUtils import AchievementsUtils
from gui.Scaleform.daapi.view.meta.PersonalCaseMeta import PersonalCaseMeta
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.genConsts.PERSONALCASECONST import PERSONALCASECONST
from gui.Scaleform.locale.CREW_SKINS import CREW_SKINS
from gui.Scaleform.locale.ITEM_TYPES import ITEM_TYPES
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.NATIONS import NATIONS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.impl import backport
from gui.impl.dialogs import dialogs
from gui.impl.dialogs.dialogs import showFreeSkillConfirmationDialog
from gui.impl.dialogs.gf_builders import ResDialogBuilder
from gui.impl.gen import R
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared import EVENT_BUS_SCOPE, events
from gui.shared.events import LoadViewEvent
from gui.shared.formatters import text_styles
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Tankman import getCrewSkinIconSmall, getCrewSkinRolePath, getCrewSkinNationPath, Tankman, getTankmanSkill
from gui.shared.gui_items.crew_skin import localizedFullName, GenderRestrictionsLocales
from gui.shared.gui_items.dossier import dumpDossier, TankmanDossier
from gui.shared.gui_items.processors.tankman import TankmanDismiss, TankmanUnload, TankmanRetraining, TankmanAddSkill, TankmanLearnFreeSkill, TankmanChangePassport, CrewSkinEquip, CrewSkinUnequip
from gui.shared.gui_items.serializers import packTankman, packVehicle, packTraining, repackTankmanWithSkinData
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.money import Money
from gui.shared.tooltips import ACTION_TOOLTIPS_TYPE
from gui.shared.tooltips.formatters import packActionTooltipData
from gui.shared.utils import decorators, roundByModulo
from gui.shared.utils.functions import getViewName, makeTooltip
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shop import showBuyGoldForCrew
from helpers import dependency
from helpers import i18n, strcmp
from items import tankmen
from items.components.crew_skins_constants import CREW_SKIN_PROPERTIES_MASKS, NO_CREW_SKIN_ID, NO_CREW_SKIN_SOUND_SET, TANKMAN_SEX
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IBootcampController, IWotPlusController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from wg_async import wg_await, wg_async
if typing.TYPE_CHECKING:
    from typing import Dict

class CrewSkinsCache(object):
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        self.__viewedItems = set()

    def initHistoricalSettings(self):
        self.__isHistoricallyAccurate, self.__isHistoricallyAccurateNeedToSync = AccountSettings.getSettings(CREW_SKINS_HISTORICAL_VISIBLE)
        if self.__isHistoricallyAccurateNeedToSync:
            self.changeHistoricalAccurate(self.settingsCore.getSetting(GAME.CUSTOMIZATION_DISPLAY_TYPE) == 0)

    def addViewedItem(self, skinID):
        self.__viewedItems.add(int(skinID))

    def changeHistoricalAccurate(self, historicallyAccurate):
        self.__isHistoricallyAccurate = historicallyAccurate
        AccountSettings.setSettings(CREW_SKINS_HISTORICAL_VISIBLE, (self.__isHistoricallyAccurate, False))

    def saveViewedData(self):
        crewSkins = AccountSettings.getSettings(CREW_SKINS_VIEWED)
        crewSkins.update(self.__viewedItems)
        AccountSettings.setSettings(CREW_SKINS_VIEWED, crewSkins)
        self.__viewedItems.clear()

    def isHistoricallyAccurate(self):
        return self.__isHistoricallyAccurate

    def checkForViewed(self, skinID):
        return skinID in self.__viewedItems


def countSkinAsNew(item):
    return item.getHistorical() if PersonalCase.crewSkinsHAConfig.isHistoricallyAccurate() else True


class PersonalCase(PersonalCaseMeta, IGlobalListener):
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    _wotPlusCtrl = dependency.descriptor(IWotPlusController)
    crewSkinsHAConfig = CrewSkinsCache()
    _SOUND_PREVIEW = 'wwsound_mode_preview01'
    _CONTEXT_HINT = 'personalCase'
    _CONTEXT_HINT_WITH_FREE_SKILLS = 'personalCaseWithFreeSkills'

    def __init__(self, ctx=None):
        super(PersonalCase, self).__init__()
        self.crewSkinsHAConfig.initHistoricalSettings()
        self.tmanInvID = ctx.get('tankmanID')
        self._tankman = self.itemsCache.items.getTankman(self.tmanInvID)
        self.__setTabID(ctx.get('page'))
        self.isBootcamp = False
        self.dataProvider = PersonalCaseDataProvider(self.tmanInvID)
        self.vehicle = self.itemsCache.items.getItemByCD(self._tankman.vehicleNativeDescr.type.compactDescr)
        self.__previewSound = None
        return

    def onPrbEntitySwitched(self):
        self.__setCommonData()

    def onPlayerStateChanged(self, entity, roster, accountInfo):
        if accountInfo.isCurrentPlayer():
            self.__setCommonData()

    def onWotPlusChanged(self, itemDiff):
        if 'isEnabled' in itemDiff:
            self.__setDossierData()

    def onUnitPlayerStateChanged(self, pInfo):
        if pInfo.isCurrentPlayer():
            self.__setCommonData()

    def onWindowClose(self):
        self.crewSkinsHAConfig.saveViewedData()
        self.destroy()

    def getCommonData(self):
        self.__setCommonData()

    def getDossierData(self):
        self.__setDossierData()

    def getRetrainingData(self):
        self.__setRetrainingData()

    def getFreeSkillsData(self):
        self.__setFreeSkillsData()

    def getSkillsData(self):
        self.__setSkillsData()

    def getDocumentsData(self):
        self.__setDocumentsData()

    def getCrewSkinsData(self):
        self.crewSkinsHAConfig.saveViewedData()
        self.__setCrewSkinsData()

    @decorators.adisp_process('updating')
    def equipCrewSkin(self, crewSkinID):
        unloader = CrewSkinEquip(self.tmanInvID, crewSkinID)
        result = yield unloader.request()
        SystemMessages.pushMessagesFromResult(result)

    def takeOffNewMarkFromCrewSkin(self, crewSkinID):
        self.crewSkinsHAConfig.addViewedItem(crewSkinID)
        self._updateNewCrewSkinsCount()

    def playCrewSkinSound(self, crewSkinID):
        crewSkin = self.itemsCache.items.getCrewSkin(crewSkinID)
        if crewSkin.getSoundSetID() != NO_CREW_SKIN_SOUND_SET:
            SoundGroups.g_instance.soundModes.setMode(crewSkin.getSoundSetID())
            sndPath = self.app.soundManager.sounds.getEffectSound(self._SOUND_PREVIEW)
            self.__previewSound = SoundGroups.g_instance.getSound2D(sndPath)
            if self.__previewSound is not None:
                self.__previewSound.play()
        return

    def updateOpenedTabID(self, tabID):
        self.tabID = tabID

    def changeHistoricallyAccurate(self, historicallyAccurate):
        self.crewSkinsHAConfig.changeHistoricalAccurate(historicallyAccurate)
        self._updateNewCrewSkinsCount()

    @decorators.adisp_process('updating')
    def unequipCrewSkin(self):
        unloader = CrewSkinUnequip(self.tmanInvID)
        result = yield unloader.request()
        SystemMessages.pushMessagesFromResult(result)

    def openChangeRoleWindow(self):
        ctx = {'tankmanID': self.tmanInvID}
        self.fireEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.ROLE_CHANGE, VIEW_ALIAS.ROLE_CHANGE), ctx=ctx), scope=EVENT_BUS_SCOPE.LOBBY)

    @decorators.adisp_process('updating')
    def dismissTankman(self, tmanInvID):
        tankman = self.__getTankmanByInvID(int(tmanInvID))
        proc = TankmanDismiss(tankman)
        result = yield proc.request()
        SystemMessages.pushMessagesFromResult(result)

    @decorators.adisp_process('retraining')
    def retrainingTankman(self, inventoryID, tankmanCostTypeIdx):
        operationCost = self.itemsCache.items.shop.tankmanCost[tankmanCostTypeIdx].get('gold', 0)
        currentGold = self.itemsCache.items.stats.gold
        if currentGold < operationCost:
            showBuyGoldForCrew(operationCost)
            return
        tankman = self.__getTankmanByInvID(int(inventoryID))
        proc = TankmanRetraining(tankman, self.vehicle, tankmanCostTypeIdx)
        result = yield proc.request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    @decorators.adisp_process('unloading')
    def unloadTankman(self, tmanInvID, currentVehicleID):
        tankman = self.__getTankmanByInvID(int(tmanInvID))
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

    @decorators.adisp_process('updating')
    def changeTankmanPassport(self, inventoryID, firstNameID, firstNameGroup, lastNameID, lastNameGroup, iconID, iconGroup):

        def checkFlashInt(value):
            return None if value == -1 else value

        firstNameID = checkFlashInt(firstNameID)
        lastNameID = checkFlashInt(lastNameID)
        iconID = checkFlashInt(iconID)
        tankman = self.__getTankmanByInvID(int(inventoryID))
        result = yield TankmanChangePassport(tankman, firstNameID, firstNameGroup, lastNameID, lastNameGroup, iconID, iconGroup).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    @decorators.adisp_process('studying')
    def addTankmanSkill(self, inventoryID, skillName):
        tankman = self.__getTankmanByInvID(int(inventoryID))
        skill = getTankmanSkill(skillName, tankman)
        processor = TankmanAddSkill(tankman, skill.name)
        result = yield processor.request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    @wg_async
    def addTankmanFreeSkill(self, inventoryID, skillName):
        tankman = self.__getTankmanByInvID(int(inventoryID))
        skill = getTankmanSkill(skillName, tankman)
        result = yield wg_await(showFreeSkillConfirmationDialog(skill=skill))
        if not result.busy:
            isOk, _ = result.result
            if isOk:
                self.__processAddTankmanFreeSkill(tankman, skillName)

    @decorators.adisp_process('studying')
    def __processAddTankmanFreeSkill(self, tankman, skillName):
        processor = TankmanLearnFreeSkill(tankman, skillName)
        result = yield processor.request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    def openExchangeFreeToTankmanXpWindow(self):
        self.fireEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.EXCHANGE_FREE_TO_TANKMAN_XP_WINDOW, getViewName(VIEW_ALIAS.EXCHANGE_FREE_TO_TANKMAN_XP_WINDOW, self.tmanInvID)), ctx={'tankManId': self.tmanInvID}), EVENT_BUS_SCOPE.LOBBY)

    def changeRetrainVehicle(self, intCD):
        self.vehicle = self.itemsCache.items.getItemByCD(intCD)
        self.__setRetrainingData()

    def dropSkills(self):
        self.fireEvent(LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.TANKMAN_SKILLS_DROP_WINDOW, getViewName(VIEW_ALIAS.TANKMAN_SKILLS_DROP_WINDOW, self.tmanInvID)), ctx={'tankmanID': self.tmanInvID}), EVENT_BUS_SCOPE.LOBBY)

    def showFreeSkillsInfo(self):
        builder = ResDialogBuilder()
        builder.setMessagesAndButtons(R.strings.dialogs.freeSkillsInfo, buttons=R.invalid)
        builder.setIcon(R.images.gui.maps.icons.tankmen.windows.freeSkillsInfoDialog())
        dialogs.show(builder.build())

    def _populate(self):
        super(PersonalCase, self)._populate()
        g_clientUpdateManager.addCallbacks({'': self.__onClientChanged})
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__hideTabsOnUpdate
        self.itemsCache.onSyncCompleted += self.__refreshData
        self._wotPlusCtrl.onDataChanged += self.onWotPlusChanged
        self.startGlobalListening()
        _hasFreeSkills = self._tankman.chosenFreeSkillsCount or self._tankman.newFreeSkillsCount
        self.setupContextHints(self._CONTEXT_HINT_WITH_FREE_SKILLS if _hasFreeSkills else self._CONTEXT_HINT, hintsArgs={'hangarTutorialPersonalCaseAdditional': (self.tmanInvID,)})
        self.addListener(events.FightButtonEvent.FIGHT_BUTTON_UPDATE, self.__updatePrbState, scope=EVENT_BUS_SCOPE.LOBBY)

    def _invalidate(self, ctx=None):
        super(PersonalCase, self)._invalidate(ctx=ctx)
        self.__setTabID(ctx.get('page'))
        self.as_openTabS(self.tabID)

    def _dispose(self):
        self.stopGlobalListening()
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__hideTabsOnUpdate
        self.itemsCache.onSyncCompleted -= self.__refreshData
        self._wotPlusCtrl.onDataChanged -= self.onWotPlusChanged
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.removeListener(events.FightButtonEvent.FIGHT_BUTTON_UPDATE, self.__updatePrbState, scope=EVENT_BUS_SCOPE.LOBBY)
        self.__stopSoundPreview()
        super(PersonalCase, self)._dispose()

    def __stopSoundPreview(self):
        if self.__previewSound is not None:
            self.__previewSound.stop()
        return

    @decorators.adisp_process('updating')
    def __setCommonData(self):
        data = yield self.dataProvider.getCommonData()
        self.__setTabID(self.tabID)
        data.update({'tabID': self.tabID,
         'isBootcamp': self.isBootcamp})
        self.as_setCommonDataS(data)

    @decorators.adisp_process('updating')
    def __setDossierData(self):
        data = yield self.dataProvider.getDossierData()
        self.as_setDossierDataS(data)

    @decorators.adisp_process('updating')
    def __setRetrainingData(self):
        data = yield self.dataProvider.getRetrainingData(self.vehicle)
        self.as_setRetrainingDataS(data)

    @decorators.adisp_process('updating')
    def __setDocumentsData(self):
        data = yield self.dataProvider.getDocumentsData()
        self.as_setDocumentsDataS(data)
        self._updateDocumentsChangeStatus()

    @decorators.adisp_process('updating')
    def __setSkillsData(self):
        data = yield self.dataProvider.getSkillsData()
        self.as_setSkillsDataS(data)

    @decorators.adisp_process('updating')
    def __setFreeSkillsData(self):
        data = yield self.dataProvider.getFreeSkillsData()
        self.as_setFreeSkillsDataS(data)

    @decorators.adisp_process('updating')
    def __setCrewSkinsData(self):
        data = yield self.dataProvider.getCrewSkinsData()
        self.as_setCrewSkinsDataS(data)
        self._updateDocumentsChangeStatus()

    def _updateDocumentsChangeStatus(self):
        changeDocumentsEnable, warning = self.dataProvider.getChangeDocumentEnableStatus()
        self.as_setDocumentsIsChangeEnableS(changeDocumentsEnable, warning)

    def _updateNewCrewSkinsCount(self):
        items = self.itemsCache.items.getItems(GUI_ITEM_TYPE.CREW_SKINS, REQ_CRITERIA.CREW_ITEM.IN_ACCOUNT)
        count = 0
        for item in items.itervalues():
            if item.isNew() and not self.crewSkinsHAConfig.checkForViewed(item.getID()) and countSkinAsNew(item):
                count += 1

        self.as_setCrewSkinsNewCountS(count)

    def __updatePrbState(self, *args):
        if not self.prbEntity.getPermissions().canChangeVehicle():
            self.destroy()

    def __onClientChanged(self, diff):
        inventory = diff.get('inventory', {})
        stats = diff.get('stats', {})
        cache = diff.get('cache', {})
        isTankmanChanged = False
        isTankmanVehicleChanged = False
        if GUI_ITEM_TYPE.CREW_SKINS in inventory:
            isTankmanChanged = True
        if GUI_ITEM_TYPE.TANKMAN in inventory:
            tankmanData = inventory[GUI_ITEM_TYPE.TANKMAN].get('compDescr')
            if tankmanData is not None and self.tmanInvID in tankmanData:
                isTankmanChanged = True
                if tankmanData[self.tmanInvID] is None:
                    return self.destroy()
            if self.tmanInvID in inventory[GUI_ITEM_TYPE.TANKMAN].get('vehicle', {}):
                isTankmanChanged = True
        if isTankmanChanged:
            self._tankman = self.itemsCache.items.getTankman(self.tmanInvID)
        isVehsLockExist = 'vehsLock' in cache
        isMoneyChanged = 'credits' in stats or 'gold' in stats or 'mayConsumeWalletResources' in cache
        isVehicleChanged = 'unlocks' in stats or isVehsLockExist or GUI_ITEM_TYPE.VEHICLE in inventory
        isFreeXpChanged = 'freeXP' in stats
        if isVehicleChanged:
            if self._tankman.isInTank:
                vehicle = self.itemsCache.items.getVehicle(self._tankman.vehicleInvID)
                if vehicle.isLocked:
                    return self.destroy()
                vehsDiff = inventory.get(GUI_ITEM_TYPE.VEHICLE, {})
                isTankmanVehicleChanged = any((vehicle.invID in hive or (vehicle.invID, '_r') in hive for hive in vehsDiff.itervalues()))
        if isTankmanChanged or isTankmanVehicleChanged or isFreeXpChanged:
            self.__setCommonData()
        if isTankmanChanged or isTankmanVehicleChanged:
            self.__setFreeSkillsData()
            self.__setSkillsData()
            self.__setDossierData()
        if isTankmanChanged or isMoneyChanged or isTankmanVehicleChanged:
            self.__setRetrainingData()
        if isTankmanChanged or isMoneyChanged:
            self.__setDocumentsData()
        if isTankmanChanged:
            self.crewSkinsHAConfig.saveViewedData()
            self.__setCrewSkinsData()
            self._updateNewCrewSkinsCount()
        return

    def __refreshData(self, reason, _):
        if reason != CACHE_SYNC_REASON.SHOP_RESYNC:
            return
        self._tankman = self.itemsCache.items.getTankman(self.tmanInvID)
        self.__setCommonData()
        self.__setFreeSkillsData()
        self.__setSkillsData()
        self.__setDossierData()
        self.__setRetrainingData()
        self.__setDocumentsData()

    def __hideTabsOnUpdate(self, _):
        if not self.lobbyContext.getServerSettings().isCrewSkinsEnabled() and self.tabID == PERSONALCASECONST.CREW_SKINS_TAB_ID:
            self.__setTabID()
            self.as_openTabS(self.tabID)
        self.__setCommonData()

    def __getTankmanByInvID(self, inventoryID):
        return self._tankman if inventoryID == self.tmanInvID else self.itemsCache.items.getTankman(inventoryID)

    def __setTabID(self, tabID=None):
        self.tabID = tabID
        if self.tabID is None:
            self.tabID = PERSONALCASECONST.STATS_TAB_ID
        elif self.tabID == PERSONALCASECONST.FREE_SKILLS_TAB_ID and self._tankman.newFreeSkillsCount <= 0:
            self.tabID = PERSONALCASECONST.SKILLS_TAB_ID
        return


class PersonalCaseDataProvider(object):
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    bootcamp = dependency.descriptor(IBootcampController)
    _wotPlusCtrl = dependency.descriptor(IWotPlusController)
    _MODIFIERS_UI_PRECISION = 2

    def __init__(self, tmanInvID):
        self.tmanInvID = tmanInvID

    @adisp_async
    def getCommonData(self, callback):
        items = self.itemsCache.items
        tankman = items.getTankman(self.tmanInvID)
        changeRoleCost = items.shop.changeRoleCost
        defaultChangeRoleCost = items.shop.defaults.changeRoleCost
        if changeRoleCost != defaultChangeRoleCost and not self.bootcamp.isInBootcamp():
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
            roleStr = i18n.makeString(TOOLTIPS.crewRole(td.role))
            tooltipChangeRole = makeTooltip(TOOLTIPS.CREW_ROLECHANGEFORBID_HEADER, i18n.makeString(TOOLTIPS.CREW_ROLECHANGEFORBID_TEXT, role=roleStr))
        showDocumentTab = not td.getRestrictions().isPassportReplacementForbidden()
        bonuses = tankman.realRoleLevel[1]
        modifiers = []
        if bonuses[0]:
            modifiers.append({'id': 'fromCommander',
             'val': bonuses[0]})
        if bonuses[1]:
            modifiers.append({'id': 'fromSkills',
             'val': self.__roundModifiers(bonuses[1])})
        if bonuses[2] or bonuses[3]:
            modifiers.append({'id': 'fromEquipment',
             'val': bonuses[2] + bonuses[3]})
        if bonuses[4]:
            modifiers.append({'id': 'penalty',
             'val': bonuses[4]})
        tankmanData = packTankman(tankman, splitFreeAndEarnedSkills=True)
        repackTankmanWithSkinData(tankman, tankmanData)
        callback({'tankman': tankmanData,
         'currentVehicle': packVehicle(currentVehicle) if currentVehicle is not None else None,
         'nativeVehicle': packVehicle(nativeVehicle),
         'isOpsLocked': isLocked,
         'lockMessage': reason,
         'modifiers': modifiers,
         'enoughFreeXPForTeaching': enoughFreeXPForTeaching,
         'tabsData': self.getTabsButtons(showDocumentTab, tankman.newFreeSkillsCount > 0),
         'tooltipDismiss': TOOLTIPS.BARRACKS_TANKMEN_DISMISS,
         'tooltipUnload': TOOLTIPS.BARRACKS_TANKMEN_UNLOAD,
         'dismissEnabled': True,
         'unloadEnabled': True,
         'changeRoleEnabled': changeRoleEnabled,
         'hasCommanderFeature': tankman.role == Tankman.ROLES.COMMANDER,
         'tooltipChangeRole': tooltipChangeRole,
         'actionChangeRole': discount})
        return

    def getTabsButtons(self, showDocumentTab, showFreeSkillsTab):
        tabs = [{'id': PERSONALCASECONST.STATS_TAB_ID,
          'label': MENU.TANKMANPERSONALCASE_TABBATTLEINFO,
          'tooltip': makeTooltip(body=MENU.TANKMANPERSONALCASE_TABBATTLEINFO),
          'linkage': PERSONALCASECONST.PERSONAL_CASE_STATS}, {'id': PERSONALCASECONST.TRAINING_TAB_ID,
          'label': MENU.TANKMANPERSONALCASE_TABTRAINING,
          'tooltip': makeTooltip(body=MENU.TANKMANPERSONALCASE_TABTRAINING),
          'linkage': PERSONALCASECONST.PERSONAL_CASE_RETRAINING}]
        if showFreeSkillsTab:
            tabs.append({'id': PERSONALCASECONST.FREE_SKILLS_TAB_ID,
             'label': MENU.TANKMANPERSONALCASE_TABFREESKILLS,
             'tooltip': makeTooltip(body=MENU.TANKMANPERSONALCASE_TABFREESKILLS),
             'linkage': PERSONALCASECONST.PERSONAL_CASE_FREE_SKILLS})
        tabs.append({'id': PERSONALCASECONST.SKILLS_TAB_ID,
         'label': MENU.TANKMANPERSONALCASE_TABSKILLS,
         'tooltip': makeTooltip(body=MENU.TANKMANPERSONALCASE_TABSKILLS),
         'linkage': PERSONALCASECONST.PERSONAL_CASE_SKILLS})
        if showDocumentTab:
            tabs.append({'id': PERSONALCASECONST.DOCS_TAB_ID,
             'label': MENU.TANKMANPERSONALCASE_TABDOCS,
             'tooltip': makeTooltip(body=MENU.TANKMANPERSONALCASE_TABDOCS),
             'linkage': PERSONALCASECONST.PERSONAL_CASE_DOCS})
            if self.lobbyContext.getServerSettings().isCrewSkinsEnabled():
                tabs.append({'id': PERSONALCASECONST.CREW_SKINS_TAB_ID,
                 'label': CREW_SKINS.FEATURE_SKINSTABHEADER,
                 'tooltip': makeTooltip(body=CREW_SKINS.FEATURE_SKINSTABHEADER),
                 'linkage': PERSONALCASECONST.PERSONAL_CASE_CREW_SKINS})
        return tabs

    @adisp_async
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

            serverSettings = self.lobbyContext.getServerSettings()
            isWotPlusEnabled = self._wotPlusCtrl.isWotPlusEnabled()
            isNewSubscriptionsEnabled = serverSettings.isWotPlusNewSubscriptionEnabled()
            hasWotPlus = self._wotPlusCtrl.isEnabled()
            secondIcon = RES_ICONS.MAPS_ICONS_CREWHEADER_ACCELERATED_CREW_TRAINING if isWotPlusEnabled else RES_ICONS.MAPS_ICONS_LIBRARY_TMAN_ACC_TRAINING_20X20
            callbackInfo = {'achievements': packedAchieves,
             'stats': tmanDossier.getStats(self.itemsCache.items.getTankman(self.tmanInvID)),
             'firstMsg': self.__makeStandardText(MENU.CONTEXTMENU_PERSONALCASE_STATS_FIRSTINFO),
             'secondMsg': self.__makeStandardText(MENU.CONTEXTMENU_PERSONALCASE_STATS_SECONDINFO),
             'secondIcon': secondIcon}
            if isWotPlusEnabled and (isNewSubscriptionsEnabled or hasWotPlus):
                callbackInfo['wotPlusIcon'] = RES_ICONS.MAPS_ICONS_CREWHEADER_INACTIVE_WOT_PLUS_CREW_IDLE
                callbackInfo['wotPlusMsg'] = self.__makeStandardText(MENU.CONTEXTMENU_PERSONALCASE_STATS_WOTPLUS)
            callback(callbackInfo)
            return

    def __makeStandardText(self, locale):
        return text_styles.standard(i18n.makeString(locale))

    @adisp_async
    def getRetrainingData(self, targetVehicle, callback):
        items = self.itemsCache.items
        tankman = items.getTankman(self.tmanInvID)
        nativeVehicleCD = tankman.vehicleNativeDescr.type.compactDescr
        maxResearchedLevel = items.stats.getMaxResearchedLevel(tankman.nationID)
        criteria = ~(~REQ_CRITERIA.UNLOCKED | ~(REQ_CRITERIA.COLLECTIBLE | REQ_CRITERIA.VEHICLE.LEVELS(range(1, maxResearchedLevel + 1))))
        criteria |= REQ_CRITERIA.NATIONS([tankman.nationID]) | ~REQ_CRITERIA.VEHICLE.OBSERVER
        criteria |= ~REQ_CRITERIA.VEHICLE.IS_CREW_LOCKED
        criteria |= ~(REQ_CRITERIA.SECRET | ~REQ_CRITERIA.INVENTORY_OR_UNLOCKED)
        criteria |= ~REQ_CRITERIA.VEHICLE.BATTLE_ROYALE
        criteria |= ~REQ_CRITERIA.VEHICLE.MAPS_TRAINING
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

    @adisp_async
    def getSkillsData(self, callback):
        tankman = self.itemsCache.items.getTankman(self.tmanInvID)
        callback(tankman.getSkillsToLearn())

    @adisp_async
    def getFreeSkillsData(self, callback):
        tankman = self.itemsCache.items.getTankman(self.tmanInvID)
        callback(tankman.getFreeSkillsToLearn())

    @adisp_async
    def getCrewSkinsData(self, callback):
        tankman = self.itemsCache.items.getTankman(self.tmanInvID)
        items = self.itemsCache.items.getItems(GUI_ITEM_TYPE.CREW_SKINS, REQ_CRITERIA.CREW_ITEM.IN_ACCOUNT)
        crewSkins = []
        newSkinsCount = 0
        if self.lobbyContext.getServerSettings().isCrewSkinsEnabled():
            for item in items.itervalues():
                uiData = self.__convertCrewSkinData(item, tankman)
                if uiData['isNew'] and countSkinAsNew(item):
                    newSkinsCount += 1
                crewSkins.append(uiData)

        callback({'crewSkins': sorted(crewSkins, key=operator.itemgetter('rarity', 'id'), reverse=True),
         'newSkinsCount': newSkinsCount,
         'historicallyAccurate': bool(PersonalCase.crewSkinsHAConfig.isHistoricallyAccurate())})

    def __convertCrewSkinData(self, crewSkin, tankman):
        cache = tankmen.g_cache.crewSkins()
        LOC_MAP = {}
        if crewSkin.getRoleID() is not None:
            LOC_MAP[CREW_SKIN_PROPERTIES_MASKS.ROLE] = i18n.makeString(ITEM_TYPES.tankman_roles(crewSkin.getRoleID()))
        if crewSkin.getSex() in TANKMAN_SEX.ALL:
            LOC_MAP[CREW_SKIN_PROPERTIES_MASKS.SEX] = backport.text(R.strings.item_types.tankman.gender.dyn(GenderRestrictionsLocales.KEYS[crewSkin.getSex()])())
        if crewSkin.getNation() is not None:
            LOC_MAP[CREW_SKIN_PROPERTIES_MASKS.NATION] = i18n.makeString(NATIONS.all(crewSkin.getNation()))
        validation, validationMask, _ = cache.validateCrewSkin(tankman.descriptor, crewSkin.getID())
        soundValidation = crewSkin.getRoleID() == tankman.role if crewSkin.getRoleID() is not None else True
        if not SoundGroups.g_instance.soundModes.currentNationalPreset[1]:
            soundValidation = False
        restrictionsMessage = backport.text(R.strings.tooltips.crewSkins.restrictions())
        if not validation:
            restrictionsLoc = list(LOC_MAP.iteritems())
            restrictionsLoc.sort(key=lambda position: position[0])
            restrictions = [ loc for key, loc in restrictionsLoc if key & validationMask ]
            restrictionsMessage += ' ' + ', '.join(restrictions)
        soundSetID = crewSkin.getSoundSetID()
        soundSetRes = R.strings.crew_skins.feature.sound.dyn(soundSetID)() if soundSetID != NO_CREW_SKIN_SOUND_SET else R.strings.crew_skins.feature.sound.noSound()
        return {'id': crewSkin.getID(),
         'fullName': localizedFullName(crewSkin),
         'description': crewSkin.getDescription(),
         'iconID': getCrewSkinIconSmall(crewSkin.getIconID()),
         'roleIconID': getCrewSkinRolePath(crewSkin.getRoleID()),
         'nationFlagIconID': getCrewSkinNationPath(crewSkin.getNation()),
         'rarity': crewSkin.getRarity(),
         'maxCount': crewSkin.getMaxCount(),
         'freeCount': crewSkin.getFreeCount(),
         'historical': crewSkin.getHistorical(),
         'soundSetID': crewSkin.getSoundSetID(),
         'useCount': len(crewSkin.getTankmenIDs()),
         'isEquip': self.tmanInvID in crewSkin.getTankmenIDs(),
         'isNew': crewSkin.isNew() and not PersonalCase.crewSkinsHAConfig.checkForViewed(crewSkin.getID()),
         'isAvailable': validation,
         'notAvailableMessage': restrictionsMessage,
         'soundSetName': backport.text(soundSetRes),
         'soundSetIsAvailable': soundValidation if crewSkin.getSoundSetID() != NO_CREW_SKIN_SOUND_SET else True}

    @adisp_async
    def getDocumentsData(self, callback):
        items = self.itemsCache.items
        tankman = items.getTankman(self.tmanInvID)
        config = tankmen.getNationConfig(tankman.nationID)
        callback({'firstName': tankman.firstUserName,
         'lastName': tankman.lastUserName,
         'firstnames': self.__getDocGroupValues(tankman, config, operator.attrgetter('firstNamesList'), config.getFirstName),
         'lastnames': self.__getDocGroupValues(tankman, config, operator.attrgetter('lastNamesList'), config.getLastName),
         'icons': self.__getDocGroupValues(tankman, config, operator.attrgetter('iconsList'), config.getIcon, sortNeeded=False)})

    def getChangeDocumentEnableStatus(self):
        if self.lobbyContext.getServerSettings().isCrewSkinsEnabled():
            tankman = self.itemsCache.items.getTankman(self.tmanInvID)
            isEnable = tankman.skinID == NO_CREW_SKIN_ID
            warning = '' if isEnable else backport.text(R.strings.crew_skins.feature.skinUsedWarning())
            return (isEnable, warning)
        return (True, '')

    @staticmethod
    def __getDocGroupValues(tankman, config, listGetter, valueGetter, sortNeeded=True):
        result = []
        isPremium, isFemale = tankman.descriptor.isPremium, tankman.descriptor.isFemale
        for gIdx, group in config.getGroups(isPremium).iteritems():
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
            return (False, backport.text(R.strings.menu.tankmen.lockReason.inbattle()))
        elif vehicle.isBroken:
            return (False, backport.text(R.strings.menu.tankmen.lockReason.broken()))
        elif vehicle.isDisabled:
            return (False, i18n.makeString('#menu:tankmen/lockReason/disabled'))
        else:
            if g_currentVehicle.item == vehicle:
                dispatcher = g_prbLoader.getDispatcher()
                if dispatcher is not None:
                    permission = dispatcher.getGUIPermissions()
                    if not permission.canChangeVehicle():
                        return (True, backport.text(R.strings.menu.tankmen.lockReason.prebattle()))
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

    def __roundModifiers(self, modifier):
        return round(modifier, self._MODIFIERS_UI_PRECISION)
