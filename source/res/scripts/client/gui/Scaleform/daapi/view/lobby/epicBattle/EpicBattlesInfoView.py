# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/epicBattle/EpicBattlesInfoView.py
import SoundGroups
from account_helpers.AccountSettings import AccountSettings, GUI_START_BEHAVIOR
from debug_utils import LOG_ERROR, LOG_CODEPOINT_WARNING
from gui import SystemMessages
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.epicBattle.epic_meta_level_icon import getEpicMetaIconVODict, EPIC_META_LEVEL_ICON_SIZE
from gui.Scaleform.daapi.view.lobby.epicBattle.epic_prestige_progress import getPrestigeProgressVO, getPrestigeLevelAwardsVOs, getFinalTankRewardIconPath, getFinalTankRewardVehicleID
from gui.Scaleform.daapi.view.lobby.epicBattle.epic_cycle_helpers import getActiveCycleTimeFrameStrings
from gui.Scaleform.daapi.view.lobby.missions.awards_formatters import AWARDS_SIZES, CurtailingAwardsComposer
from gui.Scaleform.daapi.view.meta.EpicBattlesInfoViewMeta import EpicBattlesInfoViewMeta
from gui.Scaleform.genConsts.EPICBATTLES_ALIASES import EPICBATTLES_ALIASES
from gui.Scaleform.locale.EPIC_BATTLE import EPIC_BATTLE
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.shared import EVENT_BUS_SCOPE
from gui.shared import event_dispatcher
from gui.shared import events
from gui.shared.formatters import text_styles
from gui.shared.utils import decorators
from gui.sounds.epic_sound_constants import EPIC_METAGAME_WWISE_SOUND_EVENTS
from helpers import dependency, i18n, int2roman
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IEpicBattleMetaGameController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from gui.shared.gui_items.processors.common import EpicRewardsClaimer
_META_LEVEL_TOKEN_TEMPLATE = 'epicmetagame:levelup:%d'
_ACTIVE_SKILL_POINTS_HTML_TEMPLATE = "<font face='$FieldFont' size='24' color='#fdca6a'>%d</font>"
_INACTIVE_SKILL_POINTS_HTML_TEMPLATE = "<font face='$FieldFont' size='24' color='#555555'>%d</font>"
_MAX_DISPLAYED_META_REWARDS = 4

class EpicBattlesInfoView(LobbySubView, EpicBattlesInfoViewMeta):
    epicMetaGameCtrl = dependency.descriptor(IEpicBattleMetaGameController)
    settingsCore = dependency.descriptor(ISettingsCore)
    eventsCache = dependency.descriptor(IEventsCache)
    lobbyCtx = dependency.descriptor(ILobbyContext)

    def onEscapePress(self):
        self.__close()

    def onCloseBtnClick(self):
        self.__close()

    def onManageAbilitiesBtnClick(self):
        self.fireEvent(events.LoadViewEvent(EPICBATTLES_ALIASES.EPIC_BATTLES_SKILL_ALIAS, ctx={'showBackButton': True,
         'previousPage': EPICBATTLES_ALIASES.EPIC_BATTLES_INFO_ALIAS}), EVENT_BUS_SCOPE.LOBBY)
        self.destroy()

    def onShowRewardVehicleInGarageBtnClick(self):
        self.__close()
        maxPrestigeLevel = self.lobbyCtx.getServerSettings().epicMetaGame.metaLevel.get('maxPrestigeRewardLevel', 0)
        vehID = getFinalTankRewardVehicleID(self.eventsCache.getAllQuests(), maxPrestigeLevel)
        event_dispatcher.selectVehicleInHangar(vehID)

    def onPrestigeBtnClick(self):
        if self.__canClaimFinalReward():
            self.__claimReward()
        else:
            self.fireEvent(events.LoadViewEvent(EPICBATTLES_ALIASES.EPIC_BATTLES_PRESTIGE_ALIAS), EVENT_BUS_SCOPE.LOBBY)
            self.destroy()

    def onInfoBtnClick(self):
        ctx = {'previousPage': EPICBATTLES_ALIASES.EPIC_BATTLES_INFO_ALIAS}
        self.fireEvent(events.LoadViewEvent(EPICBATTLES_ALIASES.EPIC_BATTLES_WELCOME_BACK_ALIAS, ctx=ctx), EVENT_BUS_SCOPE.LOBBY)
        self.destroy()

    def onGameRewardsBtnClick(self):
        self.fireEvent(events.LoadViewEvent(EPICBATTLES_ALIASES.EPIC_BATTLES_BROWSER_ALIAS, ctx={'urlID': 'gameRules',
         'showBackBtn': True,
         'previousPage': EPICBATTLES_ALIASES.EPIC_BATTLES_INFO_ALIAS}), EVENT_BUS_SCOPE.LOBBY)
        self.destroy()

    def _populate(self):
        super(EpicBattlesInfoView, self)._populate()
        self.as_setDataS(self._packInfoViewVO())
        defaults = AccountSettings.getFilterDefault(GUI_START_BEHAVIOR)
        stateFlags = self.settingsCore.serverSettings.getSection(GUI_START_BEHAVIOR, defaults)
        self.as_showInfoLinesS(not stateFlags['isEpicWelcomeViewShowed'])

    def _destroy(self):
        defaults = AccountSettings.getFilterDefault(GUI_START_BEHAVIOR)
        serverSettings = self.settingsCore.serverSettings
        stateFlags = serverSettings.getSection(GUI_START_BEHAVIOR, defaults)
        stateFlags['isEpicWelcomeViewShowed'] = True
        serverSettings.setSectionSettings(GUI_START_BEHAVIOR, stateFlags)
        super(EpicBattlesInfoView, self)._destroy()

    def _packCombatReservesVO(self, availablePoints):
        skillLvls = self.epicMetaGameCtrl.getSkillLevels()
        allSkills = self.epicMetaGameCtrl.getSkillInformation()
        unlockedSkills = 0
        for skillID in allSkills.iterkeys():
            if skillLvls.get(skillID, 0) != 0:
                unlockedSkills += 1

        pointsStyleTemplate = _ACTIVE_SKILL_POINTS_HTML_TEMPLATE if availablePoints > 0 else _INACTIVE_SKILL_POINTS_HTML_TEMPLATE
        return {'titleHtmlText': text_styles.highlightText(i18n.makeString(EPIC_BATTLE.INFOVIEW_COMBATRESERVES_TITLE).upper()),
         'descriptionHtmlText': text_styles.main(i18n.makeString(EPIC_BATTLE.INFOVIEW_COMBATRESERVES_DESCRIPTION)),
         'progressHtmlText': self.__getFormatedProgressHtmlText(unlockedSkills, len(allSkills)),
         'buttonText': EPIC_BATTLE.METAABILITYSCREEN_MANAGE_ABILITIES,
         'unspentPoints': availablePoints,
         'unspentHtmlPointsText': pointsStyleTemplate % availablePoints}

    def _packMetaProgressVO(self, prestigeAllowed, maxRewardClaimed):
        pPrestigeLevel, pMetaLevel, pFamePts = self.epicMetaGameCtrl.getPlayerLevelInfo()
        famePtsToProgress = self.epicMetaGameCtrl.getPointsProgressForLevel(pMetaLevel)
        rewards = []
        buttonLabel = ''
        if maxRewardClaimed:
            titleText = text_styles.highlightText(i18n.makeString(EPIC_BATTLE.INFOVIEW_PRESTIGE_CONGRATULATIONS).upper())
            descriptionText = text_styles.main(i18n.makeString(EPIC_BATTLE.INFOVIEW_PRESTIGE_ENDGAMEDESCRIPTION))
        else:
            titleText = text_styles.highlightText(i18n.makeString(EPIC_BATTLE.INFOVIEW_FAMEPOINTS_TITLE).upper())
            if self.__canClaimFinalReward():
                descriptionText = text_styles.highTitle(i18n.makeString(EPIC_BATTLE.INFOVIEW_PRESTIGE_FINALDESCRIPTION))
                buttonLabel = i18n.makeString(EPIC_BATTLE.INFOVIEW_PRESTIGE_FINALPRESTIGEBUTTONLABEL)
            elif prestigeAllowed:
                descriptionText = text_styles.highlightText(i18n.makeString(EPIC_BATTLE.INFOVIEW_PRESTIGE_DESCRIPTION) % pMetaLevel)
                buttonLabel = i18n.makeString(EPIC_BATTLE.INFOVIEW_PRESTIGE_BUTTONLABEL) % int2roman(pPrestigeLevel + 2)
            else:
                descriptionText = text_styles.main(i18n.makeString(EPIC_BATTLE.INFOVIEW_FAMEPOINTS_DESCRIPTION))
            rewards = self.__getPrestigeAwards(pPrestigeLevel + 1) if prestigeAllowed else self.__getNextMetaLevelAwards(pMetaLevel + 1)
        return {'titleHtmlText': titleText,
         'descriptionHtmlText': descriptionText,
         'buttonText': buttonLabel,
         'progressBarData': {'value': pFamePts,
                             'maxValue': famePtsToProgress},
         'famePointsText': self.__getFormatedProgressHtmlText(pFamePts, famePtsToProgress),
         'canPrestige': prestigeAllowed,
         'isEndGameState': maxRewardClaimed,
         'awards': rewards}

    def _packRewardRibbonData(self, pPrestigeLevel, allQuests, maxPrestigeLevel):
        finalRewardReached = self.__canClaimFinalReward()
        return {} if not finalRewardReached else {'rewardTitleHtmlText': text_styles.heroTitle(i18n.makeString(EPIC_BATTLE.INFOVIEW_PRESTIGE_CONGRATULATIONS).upper()),
         'epicMetaLevelIconData': None,
         'imageSource': getFinalTankRewardIconPath(allQuests, maxPrestigeLevel),
         'buttonText': EPIC_BATTLE.INFOVIEW_SHOWINGARAGE,
         'awards': self.__getPrestigeAwards(pPrestigeLevel, AWARDS_SIZES.BIG)}

    def _packInfoViewVO(self):
        pPrestigeLevel, pMetaLevel, _ = self.epicMetaGameCtrl.getPlayerLevelInfo()
        _, maxRewardClaimed = self.epicMetaGameCtrl.getSeasonData()
        maxPrestigeLevel = self.lobbyCtx.getServerSettings().epicMetaGame.metaLevel.get('maxPrestigeRewardLevel', 0)
        maxMetaLevel = self.lobbyCtx.getServerSettings().epicMetaGame.metaLevel.get('maxLevel', 0)
        prestigeAllowed = (maxPrestigeLevel < 0 or pPrestigeLevel != maxPrestigeLevel) and pMetaLevel == maxMetaLevel
        currentSeason = self.epicMetaGameCtrl.getCurrentSeason()
        cycleTimes = getActiveCycleTimeFrameStrings(currentSeason)
        if cycleTimes.startDay is not None:
            cycleDescText = '%s %s - %s' % (cycleTimes.startMonth, cycleTimes.startDay, cycleTimes.endDay)
        else:
            cycleDescText = ''
        return {'backgroundImageSrc': RES_ICONS.MAPS_ICONS_EPICBATTLES_BACKGROUNDS_META_BG,
         'smallPageTitleHtmlText': text_styles.heroTitle(i18n.makeString(EPIC_BATTLE.EPICBATTLESINFOVIEW_BATTLEMODETITLE)),
         'bigPageTitleHtmlText': text_styles.epicTitle(i18n.makeString(EPIC_BATTLE.EPICBATTLESINFOVIEW_BATTLEMODETITLE)),
         'pageDescriptionHtmlText': text_styles.promoSubTitle(cycleDescText),
         'aboutButtonLabel': i18n.makeString(EPIC_BATTLE.INFOVIEW_ABOUTBUTTON_ABOUTFRONTLINE).upper(),
         'canClaimFinalReward': self.__canClaimFinalReward(),
         'epicMetaLevelIconData': getEpicMetaIconVODict(pPrestigeLevel, pMetaLevel, EPIC_META_LEVEL_ICON_SIZE.BIG),
         'epicRewardRibbonData': self._packRewardRibbonData(pPrestigeLevel + 1, self.eventsCache.getAllQuests(), maxPrestigeLevel),
         'epicCombatReservesData': self._packCombatReservesVO(self.epicMetaGameCtrl.getSkillPoints()),
         'epicMetaProgressData': self._packMetaProgressVO(prestigeAllowed, maxRewardClaimed),
         'epicPrestigeProgressData': getPrestigeProgressVO(self.eventsCache.getAllQuests(), self.lobbyCtx.getServerSettings().epicMetaGame.metaLevel, pPrestigeLevel, prestigeAllowed)}

    @decorators.process('updating')
    def __claimReward(self):
        SoundGroups.g_instance.playSound2D(EPIC_METAGAME_WWISE_SOUND_EVENTS.EB_PRESTIGE_RESET)
        result = yield EpicRewardsClaimer().request()
        if result.userMsg:
            SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)
        elif result.success:
            self.as_showFinalRewardClaimedS()

    def __getPrestigeAwards(self, pPrestigeLevel, size=AWARDS_SIZES.SMALL):
        metaLevelComp = self.lobbyCtx.getServerSettings().epicMetaGame.metaLevel
        if pPrestigeLevel > metaLevelComp.get('maxPrestigeRewardLevel', -1):
            LOG_CODEPOINT_WARNING()
            LOG_ERROR('This line of code should never be reached!')
            self.fireEvent(events.LoadViewEvent(EPICBATTLES_ALIASES.EPIC_BATTLES_INFO_ALIAS), EVENT_BUS_SCOPE.LOBBY)
            return []
        return getPrestigeLevelAwardsVOs(self.eventsCache.getAllQuests(), pPrestigeLevel, size)

    def __getNextMetaLevelAwards(self, pMetaLevel, size=AWARDS_SIZES.SMALL):
        currentPrestigeQuest = self.eventsCache.getAllQuests().get(_META_LEVEL_TOKEN_TEMPLATE % pMetaLevel, None)
        if not currentPrestigeQuest:
            return []
        else:
            bonuses = currentPrestigeQuest.getBonuses()
            awardsFormatter = CurtailingAwardsComposer(_MAX_DISPLAYED_META_REWARDS)
            return awardsFormatter.getFormattedBonuses(bonuses, size)

    def __getFormatedProgressHtmlText(self, currentProgress, maxProgress):
        return text_styles.promoSubTitle('{} {}'.format(currentProgress, text_styles.stats('/' + str(maxProgress))))

    def __canClaimFinalReward(self):
        pPrestigeLevel, pMetaLevel, _ = self.epicMetaGameCtrl.getPlayerLevelInfo()
        _, maxRewardClaimed = self.epicMetaGameCtrl.getSeasonData()
        maxPrestigeLevel = self.lobbyCtx.getServerSettings().epicMetaGame.metaLevel.get('maxPrestigeRewardLevel', 0)
        maxMetaLevel = self.lobbyCtx.getServerSettings().epicMetaGame.metaLevel.get('maxLevel', 0)
        return pMetaLevel == maxMetaLevel and pPrestigeLevel + 1 == maxPrestigeLevel and not maxRewardClaimed

    def __close(self):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_HANGAR), scope=EVENT_BUS_SCOPE.LOBBY)
