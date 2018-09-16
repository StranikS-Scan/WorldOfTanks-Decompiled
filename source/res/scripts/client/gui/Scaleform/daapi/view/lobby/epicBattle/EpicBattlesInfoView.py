# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/epicBattle/EpicBattlesInfoView.py
from collections import namedtuple
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.EpicBattlesInfoViewMeta import EpicBattlesInfoViewMeta
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.shared import EVENT_BUS_SCOPE
from gui.shared import events
from skeletons.gui.game_control import IEpicBattleMetaGameController
from gui.Scaleform.locale.EPIC_BATTLE import EPIC_BATTLE
from helpers import i18n
from skeletons.gui.game_control import IPromoController
from gui.Scaleform.genConsts.EPICBATTLES_ALIASES import EPICBATTLES_ALIASES
from account_helpers.AccountSettings import AccountSettings, GUI_START_BEHAVIOR
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from gui.shared.formatters import text_styles
from skeletons.gui.lobby_context import ILobbyContext
from gui.Scaleform.daapi.view.lobby.epicBattle.epic_meta_level_icon import getEpicMetaIconVODict
from gui.sounds.epic_sound_constants import EPIC_METAGAME_WWISE_SOUND_EVENTS
import SoundGroups
_RULE_PANEL_DESCRIPTIONS = {0: EPIC_BATTLE.EPICBATTLESINFOVIEW_PANELDESCRIPTION_REWARDS,
 1: EPIC_BATTLE.EPICBATTLESINFOVIEW_PANELDESCRIPTION_ABILITIES,
 2: EPIC_BATTLE.EPICBATTLESINFOVIEW_PANELDESCRIPTION_BATTLEPERFORMANCE,
 3: EPIC_BATTLE.EPICBATTLESINFOVIEW_PANELDESCRIPTION_PRESTIGE}
_RULE_PANEL_HEADLINES = {0: text_styles.highTitle(i18n.makeString(EPIC_BATTLE.EPICBATTLESINFOVIEW_PANELTITLE_REWARDS)),
 1: text_styles.highTitle(i18n.makeString(EPIC_BATTLE.EPICBATTLESINFOVIEW_PANELTITLE_ABILITIES)),
 2: text_styles.highTitle(i18n.makeString(EPIC_BATTLE.EPICBATTLESINFOVIEW_PANELTITLE_BATTLEPERFORMANCE)),
 3: text_styles.highTitle(i18n.makeString(EPIC_BATTLE.EPICBATTLESINFOVIEW_PANELTITLE_PRESTIGE))}
_INDEX_TO_FRAME_NAME_STATE = {0: 'rewards',
 1: 'abilities',
 2: 'battleperformance',
 3: 'prestige'}
_RULE_PANEL_ABILITIES_INDEX = 1
_RULE_PANEL_MAX_INDEX = 3
_RULE_PANEL_INFO_STATE = 'info'
_RULE_PANEL_WELCOME_STATE = 'welcome'
_RULE_PANEL_ATTENTION_STATE = 'attention'
_RULE_PANEL_PRESTIGE_STATE = 'prestige'
_RULE_PANEL_BUTTON_LABELS = [EPIC_BATTLE.EPICBATTLESINFOVIEW_RULEREWARDSBUTTON_LABEL,
 EPIC_BATTLE.METAABILITYSCREEN_MANAGE_ABILITIES,
 EPIC_BATTLE.EPICBATTLESINFOVIEW_RULEBATTLEPERFORMANCEBUTTON_LABEL,
 EPIC_BATTLE.EPICBATTLESINFOVIEW_RULEREWARDSPRESTIGEBUTTON_LABEL]
EpicBattlesRulePanelVO = namedtuple('EpicBattlesRulePanelVO', ('imageFrame', 'panelState', 'headlineText', 'descriptionText', 'prestigeAllowed', 'skillPoints', 'buttonLabel', 'enabled'))
EpicBattlesInfoViewVO = namedtuple('EpicBattlesInfoViewVO', ('firstTimeInScreen', 'backgroundImageSrc', 'headlineTitleHtmlText', 'epicMetaLevelIconData', 'barPercentage', 'barText', 'prestigeAllowed', 'skillPoints', 'rulePanels'))

class EpicBattlesInfoView(LobbySubView, EpicBattlesInfoViewMeta):
    epicMetaGameCtrl = dependency.descriptor(IEpicBattleMetaGameController)
    settingsCore = dependency.descriptor(ISettingsCore)
    promoCtrl = dependency.descriptor(IPromoController)
    lobbyCtx = dependency.descriptor(ILobbyContext)

    def __init__(self, ctx=None):
        super(EpicBattlesInfoView, self).__init__()

    def onEscapePress(self):
        self.__close()

    def onCloseBtnClick(self):
        self.__close()

    def onButtonWelcomeAnimationDone(self):
        SoundGroups.g_instance.playSound2D(EPIC_METAGAME_WWISE_SOUND_EVENTS.EB_WELCOME_SCREEN_BUTTON_ANIM)

    def onButtonsElementWelcomeAnimationDone(self):
        SoundGroups.g_instance.playSound2D(EPIC_METAGAME_WWISE_SOUND_EVENTS.EB_WELCOME_SCREEN_MOVE)

    def onMetaElementWelcomeAnimationDone(self):
        SoundGroups.g_instance.playSound2D(EPIC_METAGAME_WWISE_SOUND_EVENTS.EB_WELCOME_SCREEN_DONE)

    def onManageAbilitiesBtnClick(self):
        self.fireEvent(events.LoadViewEvent(EPICBATTLES_ALIASES.EPIC_BATTLES_SKILL_ALIAS), EVENT_BUS_SCOPE.LOBBY)
        self.destroy()

    def onPrestigeBtnClick(self):
        self.fireEvent(events.LoadViewEvent(EPICBATTLES_ALIASES.EPIC_BATTLES_PRESTIGE_ALIAS), EVENT_BUS_SCOPE.LOBBY)
        self.destroy()

    def onSeeRewardsBtnClick(self):
        self.fireEvent(events.LoadViewEvent(EPICBATTLES_ALIASES.EPIC_BATTLES_BROWSER_ALIAS, ctx='rewards'), EVENT_BUS_SCOPE.LOBBY)
        self.destroy()

    def onReadIntroBtnClick(self):
        self.fireEvent(events.LoadViewEvent(EPICBATTLES_ALIASES.EPIC_BATTLES_BROWSER_ALIAS, ctx='intro'), EVENT_BUS_SCOPE.LOBBY)
        self.destroy()

    def _populate(self):
        super(EpicBattlesInfoView, self)._populate()
        self.as_setDataS(self._packInfoViewVO()._asdict())

    def _dispose(self):
        super(EpicBattlesInfoView, self)._dispose()

    def _packRulePanelsVO(self, firstTimeInScreen, isPrestigeAllowed, skillPoints):
        rulePanelsResult = []
        for i in range(0, _RULE_PANEL_MAX_INDEX):
            index = _RULE_PANEL_MAX_INDEX if i == 0 and isPrestigeAllowed else i
            state = _RULE_PANEL_INFO_STATE
            if firstTimeInScreen:
                state = _RULE_PANEL_WELCOME_STATE
            elif i == _RULE_PANEL_ABILITIES_INDEX and skillPoints > 0:
                state = _RULE_PANEL_ATTENTION_STATE
            elif index == _RULE_PANEL_MAX_INDEX:
                state = _RULE_PANEL_PRESTIGE_STATE
            rulePaneVO = EpicBattlesRulePanelVO(imageFrame=_INDEX_TO_FRAME_NAME_STATE[index], panelState=state, headlineText=_RULE_PANEL_HEADLINES[index], descriptionText=_RULE_PANEL_DESCRIPTIONS[index], prestigeAllowed=state == _RULE_PANEL_PRESTIGE_STATE, skillPoints=skillPoints if state == _RULE_PANEL_ATTENTION_STATE else 0, buttonLabel=_RULE_PANEL_BUTTON_LABELS[index], enabled=True)
            rulePanelsResult.append(rulePaneVO._asdict())

        return rulePanelsResult

    def _packInfoViewVO(self):
        pPrestigeLevel, pMetaLevel, pFamePts = self.epicMetaGameCtrl.getPlayerLevelInfo()
        famePtsToProgress = self.epicMetaGameCtrl.getPointsProgessForLevel(pMetaLevel)
        percentage = float(pFamePts) / float(famePtsToProgress) * 100 if famePtsToProgress > 0 else 100
        maxPrestigeLevel = self.lobbyCtx.getServerSettings().epicMetaGame.metaLevel.get('maxPrestigeLevel', 0)
        maxMetaLevel = self.lobbyCtx.getServerSettings().epicMetaGame.metaLevel.get('maxLevel', 0)
        prestigeAllowed = pPrestigeLevel != maxPrestigeLevel and pMetaLevel == maxMetaLevel
        if pMetaLevel == maxMetaLevel:
            barText = i18n.makeString(EPIC_BATTLE.EPICBATTLESINFOVIEW_MAXMETASTRING)
        else:
            barText = str(pFamePts) + text_styles.stats('/' + str(famePtsToProgress))
        defaults = AccountSettings.getFilterDefault(GUI_START_BEHAVIOR)
        filters = self.settingsCore.serverSettings.getSection(GUI_START_BEHAVIOR, defaults)
        isFirstTimeInWelcomeScreen = not filters['isEpicWelcomeViewShowed']
        return EpicBattlesInfoViewVO(firstTimeInScreen=isFirstTimeInWelcomeScreen, backgroundImageSrc=RES_ICONS.MAPS_ICONS_EPICBATTLES_BACKGROUNDS_META_BG, headlineTitleHtmlText=text_styles.heroTitle(i18n.makeString(EPIC_BATTLE.EPICBATTLESINFOVIEW_BATTLEMODETITLE)), epicMetaLevelIconData=getEpicMetaIconVODict(pPrestigeLevel, pMetaLevel), barPercentage=percentage, barText=barText, prestigeAllowed=prestigeAllowed, skillPoints=self.epicMetaGameCtrl.getSkillPoints(), rulePanels=self._packRulePanelsVO(isFirstTimeInWelcomeScreen, prestigeAllowed, self.epicMetaGameCtrl.getSkillPoints()))

    def __close(self):
        defaults = AccountSettings.getFilterDefault(GUI_START_BEHAVIOR)
        stateFlags = self.settingsCore.serverSettings.getSection(GUI_START_BEHAVIOR, defaults)
        stateFlags['isEpicWelcomeViewShowed'] = True
        self.settingsCore.serverSettings.setSectionSettings(GUI_START_BEHAVIOR, stateFlags)
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_HANGAR), scope=EVENT_BUS_SCOPE.LOBBY)
        self.destroy()
