# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/epicBattle/EpicBattlesInfoView.py
from account_helpers.AccountSettings import AccountSettings, GUI_START_BEHAVIOR
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.epicBattle.epic_cycle_helpers import getActiveCycleTimeFrameStrings
from gui.Scaleform.daapi.view.meta.EpicBattlesInfoViewMeta import EpicBattlesInfoViewMeta
from gui.Scaleform.genConsts.EPICBATTLES_ALIASES import EPICBATTLES_ALIASES
from gui.Scaleform.locale.EPIC_BATTLE import EPIC_BATTLE
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.shared import EVENT_BUS_SCOPE
from gui.shared import event_dispatcher
from gui.shared import events
from gui.shared.formatters import text_styles
from helpers import dependency, i18n
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IEpicBattleMetaGameController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
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
        event_dispatcher.selectVehicleInHangar('')

    def onPrestigeBtnClick(self):
        self.fireEvent(events.LoadViewEvent(EPICBATTLES_ALIASES.EPIC_BATTLES_PRESTIGE_ALIAS), EVENT_BUS_SCOPE.LOBBY)
        self.destroy()

    def onInfoBtnClick(self):
        ctx = {'previousPage': EPICBATTLES_ALIASES.EPIC_BATTLES_INFO_ALIAS}
        self.fireEvent(events.LoadViewEvent(EPICBATTLES_ALIASES.EPIC_BATTLES_PRESTIGE_ALIAS, ctx=ctx), EVENT_BUS_SCOPE.LOBBY)
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

    def _packInfoViewVO(self):
        currentSeason = self.epicMetaGameCtrl.getSeasonEndTime()
        cycleTimes = getActiveCycleTimeFrameStrings(currentSeason)
        if cycleTimes.startDay is not None:
            cycleDescText = '%s %s - %s' % (cycleTimes.startMonth, cycleTimes.startDay, cycleTimes.endDay)
        else:
            cycleDescText = ''
        return {'backgroundImageSrc': RES_ICONS.MAPS_ICONS_EPICBATTLES_BACKGROUNDS_META_BG,
         'smallPageTitleHtmlText': text_styles.heroTitle(i18n.makeString(EPIC_BATTLE.EPICBATTLESINFOVIEW_BATTLEMODETITLE)),
         'bigPageTitleHtmlText': text_styles.epicTitle(i18n.makeString(EPIC_BATTLE.EPICBATTLESINFOVIEW_BATTLEMODETITLE)),
         'pageDescriptionHtmlText': text_styles.promoSubTitle(cycleDescText),
         'epicPrestigeProgressData': ''}

    def __close(self):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_HANGAR), scope=EVENT_BUS_SCOPE.LOBBY)
