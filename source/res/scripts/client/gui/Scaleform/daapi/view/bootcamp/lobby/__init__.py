# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/lobby/__init__.py
from bootcamp.Bootcamp import g_bootcamp
from gui.app_loader.settings import APP_NAME_SPACE
from gui.shared import EVENT_BUS_SCOPE, g_eventBus
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import ViewSettings, GroupedViewSettings, ViewTypes, ScopeTemplates
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.shared.events import BootcampEvent, LoadEvent, LoadViewEvent
from gui.Scaleform.genConsts.BOOTCAMP_ALIASES import BOOTCAMP_ALIASES

def getContextMenuHandlers():
    pass


def getViewSettings():
    from gui.Scaleform.daapi.view.bootcamp.BCOutroVideoPage import BCOutroVideoPage
    from gui.Scaleform.daapi.view.bootcamp.BCBattleResult import BCBattleResult
    from gui.Scaleform.daapi.view.bootcamp.BCTooltipsWindow import BCTooltipsWindow
    from gui.Scaleform.daapi.view.bootcamp.BCLobbyView import BCLobbyView
    from gui.Scaleform.daapi.view.bootcamp.BCMessageWindow import BCMessageWindow
    from gui.Scaleform.daapi.view.bootcamp.BCResearch import BCResearch
    from gui.Scaleform.daapi.view.bootcamp.BCTechTree import BCTechTree
    from gui.Scaleform.daapi.view.bootcamp.BCVehiclePreview import BCVehiclePreview
    from gui.Scaleform.daapi.view.bootcamp.BCHighlights import BCHighlights
    from gui.Scaleform.daapi.view.bootcamp.BCNationsWindow import BCNationsWindow
    from gui.Scaleform.daapi.view.bootcamp.BCVehicleBuyWindow import BCVehicleBuyWindow
    from gui.Scaleform.daapi.view.bootcamp.BCVehicleBuyView import BCVehicleBuyView
    from gui.Scaleform.daapi.view.bootcamp.BCTechnicalMaintenance import BCTechnicalMaintenance
    from gui.Scaleform.daapi.view.bootcamp.BCFittingPopover import BCFittingPopover
    from gui.Scaleform.daapi.view.bootcamp.BCPersonalCase import BCPersonalCase
    from gui.Scaleform.daapi.view.bootcamp.BCQuestsControl import BCQuestsControl
    from gui.Scaleform.daapi.view.bootcamp.BCQuestsWindow import BCQuestsWindow
    from gui.Scaleform.daapi.view.bootcamp.BCBattleSelector import BCBattleSelector
    from gui.Scaleform.daapi.view.bootcamp.BCAppearManager import BCAppearManager
    from gui.Scaleform.daapi.view.bootcamp.BCQueueDialog import BCQueueDialog
    return (ViewSettings(VIEW_ALIAS.BOOTCAMP_OUTRO_VIDEO, BCOutroVideoPage, 'BCOutroVideo.swf', ViewTypes.TOP_WINDOW, None, ScopeTemplates.TOP_WINDOW_SCOPE),
     ViewSettings(VIEW_ALIAS.BOOTCAMP_BATTLE_RESULT, BCBattleResult, 'BCBattleResult.swf', ViewTypes.TOP_WINDOW, None, ScopeTemplates.TOP_WINDOW_SCOPE),
     ViewSettings(VIEW_ALIAS.BOOTCAMP_TOOLTIPS_WINDOW, BCTooltipsWindow, 'BCTooltipsWindow.swf', ViewTypes.WINDOW, None, ScopeTemplates.TOP_WINDOW_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.BOOTCAMP_MESSAGE_WINDOW, BCMessageWindow, 'BCMessageWindow.swf', ViewTypes.WINDOW, '', None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.BOOTCAMP_LOBBY_RESEARCH, BCResearch, 'research.swf', ViewTypes.LOBBY_SUB, VIEW_ALIAS.BOOTCAMP_LOBBY_RESEARCH, ScopeTemplates.DEFAULT_SCOPE, True),
     ViewSettings(VIEW_ALIAS.BOOTCAMP_LOBBY_TECHTREE, BCTechTree, 'techTree.swf', ViewTypes.LOBBY_SUB, VIEW_ALIAS.BOOTCAMP_LOBBY_TECHTREE, ScopeTemplates.DEFAULT_SCOPE, True),
     ViewSettings(VIEW_ALIAS.BOOTCAMP_LOBBY_HIGHLIGHTS, BCHighlights, 'BCHighlights.swf', ViewTypes.LOBBY_TOP_SUB, VIEW_ALIAS.BOOTCAMP_LOBBY_HIGHLIGHTS, ScopeTemplates.DEFAULT_SCOPE, True),
     ViewSettings(VIEW_ALIAS.BOOTCAMP_NATIONS_WINDOW, BCNationsWindow, 'BCNationsWindow.swf', ViewTypes.WINDOW, VIEW_ALIAS.BOOTCAMP_NATIONS_WINDOW, ScopeTemplates.DEFAULT_SCOPE, True),
     GroupedViewSettings(VIEW_ALIAS.BOOTCAMP_PERSONAL_CASE, BCPersonalCase, 'BCPersonalCase.swf', ViewTypes.WINDOW, 'personalCaseWindow', None, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.BOOTCAMP_VEHICLE_PREVIEW, BCVehiclePreview, 'vehiclePreview.swf', ViewTypes.LOBBY_SUB, VIEW_ALIAS.BOOTCAMP_VEHICLE_PREVIEW, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.BOOTCAMP_VEHICLE_BUY_WINDOW, BCVehicleBuyWindow, 'BCVehicleBuyWindow.swf', ViewTypes.TOP_WINDOW, None, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.BOOTCAMP_VEHICLE_BUY_VIEW, BCVehicleBuyView, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.BOOTCAMP_TECHNICAL_MAINTENANCE, BCTechnicalMaintenance, 'BCTechnicalMaintenance.swf', ViewTypes.WINDOW, None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.BOOTCAMP_FITTING_SELECT_POPOVER, BCFittingPopover, 'fittingSelectPopover.swf', ViewTypes.WINDOW, VIEW_ALIAS.BOOTCAMP_FITTING_SELECT_POPOVER, VIEW_ALIAS.BOOTCAMP_FITTING_SELECT_POPOVER, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.BOOTCAMP_BATTLE_TYPE_SELECT_POPOVER, BCBattleSelector, 'itemSelectorPopover.swf', ViewTypes.WINDOW, VIEW_ALIAS.BOOTCAMP_BATTLE_TYPE_SELECT_POPOVER, VIEW_ALIAS.BOOTCAMP_BATTLE_TYPE_SELECT_POPOVER, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.BOOTCAMP_QUEUE_DIALOG, BCQueueDialog, 'BCQueueWindow.swf', ViewTypes.TOP_WINDOW, '', None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.BOOTCAMP_QUESTS_CONTROL, BCQuestsControl, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BOOTCAMP_ALIASES.BOOTCAMP_APPEAR_MANAGER, BCAppearManager, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.BOOTCAMP_QUESTS_WINDOW, BCQuestsWindow, 'BCQuestsWindow.swf', ViewTypes.WINDOW, None, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (BootcampPackageBusinessHandler(),)


class BootcampPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((VIEW_ALIAS.BOOTCAMP_LOBBY_OVERLAY_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.BOOTCAMP_INTRO_VIDEO, self.loadViewByCtxEvent),
         (VIEW_ALIAS.BOOTCAMP_OUTRO_VIDEO, self.loadViewByCtxEvent),
         (VIEW_ALIAS.BOOTCAMP_BATTLE_RESULT, self.loadViewByCtxEvent),
         (VIEW_ALIAS.BOOTCAMP_TOOLTIPS_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.LOBBY, self.loadViewByCtxEvent),
         (VIEW_ALIAS.BOOTCAMP_MESSAGE_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.BOOTCAMP_LOBBY_HIGHLIGHTS, self.loadViewByCtxEvent),
         (VIEW_ALIAS.BOOTCAMP_LOBBY_RESEARCH, self.__loadResearch),
         (VIEW_ALIAS.BOOTCAMP_LOBBY_TECHTREE, self.loadViewByCtxEvent),
         (VIEW_ALIAS.BOOTCAMP_NATIONS_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.BOOTCAMP_PERSONAL_CASE, self.loadViewByCtxEvent),
         (VIEW_ALIAS.BOOTCAMP_VEHICLE_PREVIEW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.BOOTCAMP_VEHICLE_BUY_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.BOOTCAMP_TECHNICAL_MAINTENANCE, self.loadViewByCtxEvent),
         (VIEW_ALIAS.BOOTCAMP_FITTING_SELECT_POPOVER, self.loadViewByCtxEvent),
         (VIEW_ALIAS.BOOTCAMP_QUESTS_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.BOOTCAMP_BATTLE_TYPE_SELECT_POPOVER, self.onBattleTypeSelectPopover),
         (LoadEvent.EXIT_FROM_RESEARCH, self.__exitFromResearch),
         (BootcampEvent.ADD_HIGHLIGHT, self.onShowHint),
         (BootcampEvent.REMOVE_HIGHLIGHT, self.onHideHint),
         (BootcampEvent.REMOVE_ALL_HIGHLIGHTS, self.onHideAllHints),
         (BootcampEvent.HINT_COMPLETE, self.onComplete),
         (BootcampEvent.HINT_HIDE, self.onHide),
         (BootcampEvent.HINT_CLOSE, self.onClose),
         (BootcampEvent.SET_VISIBLE_ELEMENTS, self.setVisibleElements),
         (BootcampEvent.SHOW_NEW_ELEMENTS, self.showNewElements),
         (BootcampEvent.QUEUE_DIALOG_SHOW, self.queueDialogShow),
         (BootcampEvent.QUEUE_DIALOG_CLOSE, self.queueDialogClose))
        super(BootcampPackageBusinessHandler, self).__init__(listeners, APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
        self.__exitEvent = None
        return

    def onGarageLessonCompleted(self):
        pass

    def onHideAllHints(self, event):
        hintWindow = self.findViewByAlias(ViewTypes.LOBBY_TOP_SUB, VIEW_ALIAS.BOOTCAMP_LOBBY_HIGHLIGHTS)
        if hintWindow is not None:
            hintWindow.hideAllHints()
        return

    def onHideHint(self, event):
        hintWindow = self.findViewByAlias(ViewTypes.LOBBY_TOP_SUB, VIEW_ALIAS.BOOTCAMP_LOBBY_HIGHLIGHTS)
        if hintWindow is not None:
            hintWindow.hideHint(event.ctx)
        return

    def onShowHint(self, event):
        hintWindow = self.findViewByAlias(ViewTypes.LOBBY_TOP_SUB, VIEW_ALIAS.BOOTCAMP_LOBBY_HIGHLIGHTS)
        if hintWindow is not None:
            hintWindow.showHint(event.ctx)
        return

    def onHide(self, event):
        hintWindow = self.findViewByAlias(ViewTypes.WINDOW, VIEW_ALIAS.BOOTCAMP_TOOLTIPS_WINDOW)
        if hintWindow is not None:
            hintWindow.as_hideHandlerS()
        return

    def onComplete(self, event):
        hintWindow = self.findViewByAlias(ViewTypes.WINDOW, VIEW_ALIAS.BOOTCAMP_TOOLTIPS_WINDOW)
        if hintWindow is not None:
            hintWindow.as_completeHandlerS()
        return

    def onClose(self, event):
        hintWindow = self.findViewByAlias(ViewTypes.WINDOW, VIEW_ALIAS.BOOTCAMP_TOOLTIPS_WINDOW)
        if hintWindow is not None:
            hintWindow.destroy()
        return

    def __exitFromResearch(self, _):
        if self.__exitEvent is not None:
            g_eventBus.handleEvent(self.__exitEvent, scope=EVENT_BUS_SCOPE.LOBBY)
        return

    def showNewElements(self, event):
        ctx = event.ctx
        lobbyView = self.findViewByAlias(ViewTypes.DEFAULT, VIEW_ALIAS.LOBBY)
        lobbyHangar = self.findViewByAlias(ViewTypes.LOBBY_SUB, VIEW_ALIAS.LOBBY_HANGAR)
        if lobbyHangar is not None:
            lobbyHangar.showNewElements(ctx)
        if lobbyView is not None:
            lobbyView.showNewElements(ctx)
        return

    def setVisibleElements(self, event):
        ctx = event.ctx
        lobbyView = self.findViewByAlias(ViewTypes.DEFAULT, VIEW_ALIAS.LOBBY)
        lobbyHangar = self.findViewByAlias(ViewTypes.LOBBY_SUB, VIEW_ALIAS.LOBBY_HANGAR)
        if lobbyView is not None:
            lobbyView.updateVisibleComponents(ctx)
        if lobbyHangar is not None:
            lobbyHangar.updateVisibleComponents(ctx)
        return

    def onBattleTypeSelectPopover(self, event):
        self.loadViewByCtxEvent(event)
        from bootcamp.BootcampGarage import g_bootcampGarage
        if g_bootcampGarage.getPrevHint() == 'highlightButton_BattleType_LessonV':
            g_bootcampGarage.hidePrevShowNextHint()

    def queueDialogShow(self, event):
        ctx = {'backgroundImage': '../maps/login/back_25_without_sparks.png',
         'lessonNumber': g_bootcamp.getLessonNum(),
         'timeout': g_bootcamp.getContextIntParameter('lessonQueueTimeout', 15)}
        queueDialog = self.findViewByAlias(ViewTypes.TOP_WINDOW, VIEW_ALIAS.BOOTCAMP_QUEUE_DIALOG)
        if queueDialog:
            queueDialog.updateSettings(ctx)
            return
        self.loadViewByCtxEvent(LoadViewEvent(VIEW_ALIAS.BOOTCAMP_QUEUE_DIALOG, ctx=ctx))

    def queueDialogClose(self, event):
        queueDialog = self.findViewByAlias(ViewTypes.TOP_WINDOW, VIEW_ALIAS.BOOTCAMP_QUEUE_DIALOG)
        if queueDialog:
            queueDialog.destroy()

    def __loadResearch(self, event):
        ctx = event.ctx
        self.__exitEvent = ctx.get('exit')
        self.loadViewWithDefName(VIEW_ALIAS.BOOTCAMP_LOBBY_RESEARCH, ctx=ctx)

    def __loadSimpleDialog(self, event):
        pass
