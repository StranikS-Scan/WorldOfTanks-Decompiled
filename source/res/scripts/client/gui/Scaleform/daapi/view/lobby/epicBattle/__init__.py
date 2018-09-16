# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/epicBattle/__init__.py
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework import ViewSettings, ViewTypes
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.EPICBATTLES_ALIASES import EPICBATTLES_ALIASES
from gui.app_loader.settings import APP_NAME_SPACE
from gui.shared import EVENT_BUS_SCOPE

def getContextMenuHandlers():
    pass


def getViewSettings():
    from gui.Scaleform.daapi.view.lobby.epicBattle.EpicBattlesSkillView import EpicBattlesSkillView
    from gui.Scaleform.daapi.view.lobby.epicBattle.EpicBattlesAfterBattleView import EpicBattlesAfterBattleView
    from gui.Scaleform.daapi.view.lobby.epicBattle.EpicBattlesInfoView import EpicBattlesInfoView
    from gui.Scaleform.daapi.view.lobby.epicBattle.EpicBattlesPrestigeView import EpicBattlesPrestigeView
    from gui.Scaleform.daapi.view.lobby.epicBattle.EpicBattlesBrowserView import EpicBattlesBrowserView
    return (ViewSettings(EPICBATTLES_ALIASES.EPIC_BATTLES_SKILL_ALIAS, EpicBattlesSkillView, EPICBATTLES_ALIASES.EPIC_BATTLES_SKILL_VIEW_UI, ViewTypes.LOBBY_SUB, EPICBATTLES_ALIASES.EPIC_BATTLES_SKILL_ALIAS, ScopeTemplates.LOBBY_SUB_SCOPE, True),
     ViewSettings(EPICBATTLES_ALIASES.EPIC_BATTLES_AFTER_BATTLE_ALIAS, EpicBattlesAfterBattleView, EPICBATTLES_ALIASES.EPIC_BATTLES_AFTER_BATTLE_UI, ViewTypes.OVERLAY, EPICBATTLES_ALIASES.EPIC_BATTLES_AFTER_BATTLE_ALIAS, ScopeTemplates.OVERLAY_SCOPE, True),
     ViewSettings(EPICBATTLES_ALIASES.EPIC_BATTLES_INFO_ALIAS, EpicBattlesInfoView, EPICBATTLES_ALIASES.EPIC_BATTLES_INFO_VIEW_UI, ViewTypes.LOBBY_SUB, EPICBATTLES_ALIASES.EPIC_BATTLES_INFO_ALIAS, ScopeTemplates.LOBBY_SUB_SCOPE, True),
     ViewSettings(EPICBATTLES_ALIASES.EPIC_BATTLES_PRESTIGE_ALIAS, EpicBattlesPrestigeView, EPICBATTLES_ALIASES.EPIC_BATTLES_PRESTIGE_INFO_VIEW_UI, ViewTypes.LOBBY_SUB, EPICBATTLES_ALIASES.EPIC_BATTLES_PRESTIGE_ALIAS, ScopeTemplates.LOBBY_SUB_SCOPE, True),
     ViewSettings(EPICBATTLES_ALIASES.EPIC_BATTLES_BROWSER_ALIAS, EpicBattlesBrowserView, EPICBATTLES_ALIASES.EPIC_BATTLES_BROWSER_UI, ViewTypes.LOBBY_SUB, EPICBATTLES_ALIASES.EPIC_BATTLES_BROWSER_ALIAS, ScopeTemplates.LOBBY_SUB_SCOPE, True))


def getBusinessHandlers():
    return (EpicMetaGamePackageBusinessHandler(),)


class EpicMetaGamePackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((EPICBATTLES_ALIASES.EPIC_BATTLES_SKILL_ALIAS, self.loadViewByCtxEvent),
         (EPICBATTLES_ALIASES.EPIC_BATTLES_AFTER_BATTLE_ALIAS, self.loadViewByCtxEvent),
         (EPICBATTLES_ALIASES.EPIC_BATTLES_INFO_ALIAS, self.loadViewByCtxEvent),
         (EPICBATTLES_ALIASES.EPIC_BATTLES_PRESTIGE_ALIAS, self.loadViewByCtxEvent),
         (EPICBATTLES_ALIASES.EPIC_BATTLES_BROWSER_ALIAS, self.loadViewByCtxEvent))
        super(EpicMetaGamePackageBusinessHandler, self).__init__(listeners, APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
