# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/epicBattle/EpicBattlesInfoView.py
from collections import namedtuple
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.EpicBattlesInfoViewMeta import EpicBattlesInfoViewMeta
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
EpicBattlesInfoViewVO = namedtuple('EpicBattlesInfoViewVO', ('firstTimeInScreen', 'backgroundImageSrc', 'epicMetaLevelIconData', 'barPercentage', 'barText', 'prestigeAllowed', 'skillPoints'))

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

    def onManageAbilitiesBtnClick(self):
        self.fireEvent(events.LoadViewEvent(EPICBATTLES_ALIASES.EPIC_BATTLES_SKILL_ALIAS), EVENT_BUS_SCOPE.LOBBY)
        self.destroy()

    def onPrestigeBtnClick(self):
        self.fireEvent(events.LoadViewEvent(EPICBATTLES_ALIASES.EPIC_BATTLES_PRESTIGE_ALIAS), EVENT_BUS_SCOPE.LOBBY)
        self.destroy()

    def onSeeRewardsBtnClick(self):
        seeRewardsUrl = 'https://worldoftanks.eu/'
        self.promoCtrl.showPromo(seeRewardsUrl, '', True)

    def onReadIntroBtnClick(self):
        readIntroUrl = 'https://worldoftanks.eu/en/news/'
        self.promoCtrl.showPromo(readIntroUrl, '', True)

    def _populate(self):
        super(EpicBattlesInfoView, self)._populate()
        self.as_setStaticTextsS(self._packTranslations())
        self.as_setDataS(self._packInfoViewVO()._asdict())

    def _dispose(self):
        super(EpicBattlesInfoView, self)._dispose()

    def _packTranslations(self):
        return {'battleModeTitle': text_styles.superPromoTitle(i18n.makeString(EPIC_BATTLE.EPICBATTLESINFOVIEW_BATTLEMODETITLE)),
         'rewards': text_styles.highTitle(i18n.makeString(EPIC_BATTLE.EPICBATTLESINFOVIEW_PANELTITLE_REWARDS)),
         'abilities': text_styles.highTitle(i18n.makeString(EPIC_BATTLE.EPICBATTLESINFOVIEW_PANELTITLE_ABILITIES)),
         'battlePerformance': text_styles.highTitle(i18n.makeString(EPIC_BATTLE.EPICBATTLESINFOVIEW_PANELTITLE_BATTLEPERFORMANCE)),
         'prestige': text_styles.highTitle(i18n.makeString(EPIC_BATTLE.EPICBATTLESINFOVIEW_PANELTITLE_PRESTIGE))}

    def _packInfoViewVO(self):
        pPrestigeLevel, pMetaLevel, pFamePts = self.epicMetaGameCtrl.getPlayerLevelInfo()
        famePtsToProgress = self.epicMetaGameCtrl.getPointsProgessForLevel(pMetaLevel)
        percentage = float(pFamePts) / float(famePtsToProgress) * 100 if famePtsToProgress > 0 else 100
        maxPrestigeLevel = self.lobbyCtx.getServerSettings().epicMetaGame.metaLevel.get('maxPrestigeLevel', 0)
        maxMetaLevel = self.lobbyCtx.getServerSettings().epicMetaGame.metaLevel.get('maxLevel', 0)
        prestigeAllowed = pPrestigeLevel != maxPrestigeLevel and pMetaLevel == maxMetaLevel
        defaults = AccountSettings.getFilterDefault(GUI_START_BEHAVIOR)
        filters = self.settingsCore.serverSettings.getSection(GUI_START_BEHAVIOR, defaults)
        return EpicBattlesInfoViewVO(firstTimeInScreen=not filters['isEpicWelcomeViewShowed'], backgroundImageSrc='../maps/icons/epicBattles/backgrounds/meta_bg.jpg', epicMetaLevelIconData=getEpicMetaIconVODict(pPrestigeLevel, pMetaLevel), barPercentage=percentage, barText='{}{}'.format(str(pFamePts), text_styles.stats('/' + str(famePtsToProgress))), prestigeAllowed=prestigeAllowed, skillPoints=self.epicMetaGameCtrl.getSkillPoints())

    def __close(self):
        defaults = AccountSettings.getFilterDefault(GUI_START_BEHAVIOR)
        stateFlags = self.settingsCore.serverSettings.getSection(GUI_START_BEHAVIOR, defaults)
        stateFlags['isEpicWelcomeViewShowed'] = True
        self.settingsCore.serverSettings.setSectionSettings(GUI_START_BEHAVIOR, stateFlags)
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_HANGAR), scope=EVENT_BUS_SCOPE.LOBBY)
        self.destroy()
