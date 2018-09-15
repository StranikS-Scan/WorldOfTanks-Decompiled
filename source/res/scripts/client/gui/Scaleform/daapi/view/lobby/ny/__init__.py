# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/ny/__init__.py
from gui.Scaleform.daapi.view.lobby.ny.ny_rewards import NYRecruitWindow
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import ViewSettings, GroupedViewSettings, ViewTypes, ScopeTemplates
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.app_loader.settings import APP_NAME_SPACE
from gui.shared import EVENT_BUS_SCOPE

def getContextMenuHandlers():
    from gui.Scaleform.daapi.view.lobby.ny import ny_cm_handlers
    return ((CONTEXT_MENU_HANDLER_TYPE.NY_TOY, ny_cm_handlers.NyToyContextMenuHandler), (CONTEXT_MENU_HANDLER_TYPE.NY_CURRENT_TOY, ny_cm_handlers.NyCurrentToyContextMenuHandler), (CONTEXT_MENU_HANDLER_TYPE.NY_TOY_SLOT, ny_cm_handlers.NyToySlotContextMenuHandler))


def getViewSettings():
    from gui.Scaleform.daapi.view.lobby.ny.ny_screen import NYScreen
    from gui.Scaleform.daapi.view.lobby.ny.ny_rewards import NYRewards
    from gui.Scaleform.daapi.view.lobby.ny.ny_rewards import NYApplyDiscountOnVehiclePopup
    from gui.Scaleform.daapi.view.lobby.ny.ny_craft import NYCraft
    from gui.Scaleform.daapi.view.lobby.ny.ny_break import NY_Break
    from gui.Scaleform.daapi.view.lobby.ny.ny_chests_view import NYChestsView
    from gui.Scaleform.daapi.view.lobby.ny.ny_box_popover import NYBoxPopover
    from gui.Scaleform.daapi.view.lobby.ny.ny_decorations_popover import NYDecorationsPopover
    from gui.Scaleform.daapi.view.lobby.ny.ny_screen_view_tree import NYScreenViewTree
    from gui.Scaleform.daapi.view.lobby.ny.ny_screen_view_snowman import NYScreenViewSnowman
    from gui.Scaleform.daapi.view.lobby.ny.ny_screen_view_house import NYScreenViewHouse
    from gui.Scaleform.daapi.view.lobby.ny.ny_screen_view_light import NYScreenViewLight
    from gui.Scaleform.daapi.view.lobby.ny.ny_craft_popover import NYCraftPopover
    from gui.Scaleform.daapi.view.lobby.ny.ny_level_up import NYLevelUp
    from gui.Scaleform.daapi.view.lobby.ny.ny_mission_reward_window import NYMissionRewardWindow
    from gui.Scaleform.daapi.view.lobby.ny.ny_mission_reward_screen import NYMissionRewardScreen
    from gui.Scaleform.daapi.view.lobby.ny.ny_collections_groups import NYCollectionsGroups
    from gui.Scaleform.daapi.view.lobby.ny.ny_collections import NYCollections
    return (ViewSettings(VIEW_ALIAS.LOBBY_NY_SCREEN, NYScreen, 'nyScreen.swf', ViewTypes.LOBBY_SUB, VIEW_ALIAS.LOBBY_NY_SCREEN, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.LOBBY_NY_REWARDS, NYRewards, 'nyScreenRewards.swf', ViewTypes.LOBBY_SUB, VIEW_ALIAS.LOBBY_NY_REWARDS, ScopeTemplates.LOBBY_SUB_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.NY_RECRUIT_WINDOW, NYRecruitWindow, 'questRecruitWindow.swf', ViewTypes.WINDOW, VIEW_ALIAS.NY_RECRUIT_WINDOW, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.LOBBY_NY_CRAFT, NYCraft, 'nyScreenCraft.swf', ViewTypes.LOBBY_SUB, VIEW_ALIAS.LOBBY_NY_CRAFT, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.LOBBY_NY_BREAK, NY_Break, 'nyScreenBreak.swf', ViewTypes.LOBBY_SUB, VIEW_ALIAS.LOBBY_NY_BREAK, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.LOBBY_NY_CHESTS, NYChestsView, 'nyChestsView.swf', ViewTypes.LOBBY_SUB, VIEW_ALIAS.LOBBY_NY_CHESTS, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.NY_LEVEL_UP, NYLevelUp, 'nyScreenLevelUp.swf', ViewTypes.OVERLAY, VIEW_ALIAS.NY_LEVEL_UP, ScopeTemplates.LOBBY_TOP_SUB_SCOPE, True),
     ViewSettings(VIEW_ALIAS.LOBBY_NY_MISSIONS_REWARD_RECEIPT, NYMissionRewardScreen, 'nyMissionRewardScreen.swf', ViewTypes.OVERLAY, VIEW_ALIAS.LOBBY_NY_MISSIONS_REWARD_RECEIPT, ScopeTemplates.LOBBY_TOP_SUB_SCOPE, True),
     ViewSettings(VIEW_ALIAS.LOBBY_NY_COLLECTIONS_GROUP, NYCollectionsGroups, 'nyCollectionsGroups.swf', ViewTypes.LOBBY_SUB, VIEW_ALIAS.LOBBY_NY_COLLECTIONS_GROUP, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.LOBBY_NY_COLLECTIONS, NYCollections, 'nyCollections.swf', ViewTypes.LOBBY_SUB, VIEW_ALIAS.LOBBY_NY_COLLECTIONS, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.NY_TREE, NYScreenViewTree, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.NY_SNOWMAN, NYScreenViewSnowman, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.NY_HOUSE, NYScreenViewHouse, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.NY_LIGHT, NYScreenViewLight, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.NY_BOX_POPOVER, NYBoxPopover, 'nyBoxPopover.swf', ViewTypes.WINDOW, VIEW_ALIAS.NY_BOX_POPOVER, VIEW_ALIAS.NY_BOX_POPOVER, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.NY_DECORATIONS_POPOVER, NYDecorationsPopover, 'nyDecorationsPopover.swf', ViewTypes.WINDOW, VIEW_ALIAS.NY_DECORATIONS_POPOVER, VIEW_ALIAS.NY_DECORATIONS_POPOVER, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.NY_CRAFT_POPOVER, NYCraftPopover, 'nyCraftPopover.swf', ViewTypes.WINDOW, VIEW_ALIAS.NY_CRAFT_POPOVER, VIEW_ALIAS.NY_CRAFT_POPOVER, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.LOBBY_NY_MISSIONS_REWARD, NYMissionRewardWindow, 'nyMissionRewardWindow.swf', ViewTypes.WINDOW, VIEW_ALIAS.LOBBY_NY_MISSIONS_REWARD, VIEW_ALIAS.LOBBY_NY_MISSIONS_REWARD, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.NY_APPLY_DISCOUNT_FILTER, NYApplyDiscountOnVehiclePopup, 'vehicleSelector.swf', ViewTypes.TOP_WINDOW, '', None, ScopeTemplates.DEFAULT_SCOPE, True, isModal=True))


def getBusinessHandlers():
    return (NYPackageBusinessHandler(),)


class NYPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((VIEW_ALIAS.NY_CRAFT_POPOVER, self.loadViewByCtxEvent),
         (VIEW_ALIAS.NY_APPLY_DISCOUNT_FILTER, self.loadViewByCtxEvent),
         (VIEW_ALIAS.NY_BOX_POPOVER, self.loadViewByCtxEvent),
         (VIEW_ALIAS.NY_DECORATIONS_POPOVER, self.loadViewByCtxEvent),
         (VIEW_ALIAS.LOBBY_NY_SCREEN, self.loadViewByCtxEvent),
         (VIEW_ALIAS.LOBBY_NY_REWARDS, self.loadViewByCtxEvent),
         (VIEW_ALIAS.NY_RECRUIT_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.LOBBY_NY_CRAFT, self.loadViewByCtxEvent),
         (VIEW_ALIAS.LOBBY_NY_BREAK, self.loadViewByCtxEvent),
         (VIEW_ALIAS.LOBBY_NY_CHESTS, self.loadViewByCtxEvent),
         (VIEW_ALIAS.NY_TREE, self.loadViewByCtxEvent),
         (VIEW_ALIAS.NY_SNOWMAN, self.loadViewByCtxEvent),
         (VIEW_ALIAS.NY_HOUSE, self.loadViewByCtxEvent),
         (VIEW_ALIAS.NY_LIGHT, self.loadViewByCtxEvent),
         (VIEW_ALIAS.NY_LEVEL_UP, self.loadViewByCtxEvent),
         (VIEW_ALIAS.LOBBY_NY_MISSIONS_REWARD, self.loadViewByCtxEvent),
         (VIEW_ALIAS.LOBBY_NY_MISSIONS_REWARD_RECEIPT, self.loadViewByCtxEvent),
         (VIEW_ALIAS.LOBBY_NY_COLLECTIONS_GROUP, self.loadViewByCtxEvent),
         (VIEW_ALIAS.LOBBY_NY_COLLECTIONS, self.loadViewByCtxEvent))
        super(NYPackageBusinessHandler, self).__init__(listeners, APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
