# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/lobby/__init__.py
from bootcamp.Bootcamp import g_bootcamp
from gui.app_loader import settings as app_settings
from gui.shared import EVENT_BUS_SCOPE, g_eventBus
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import ViewSettings, GroupedViewSettings, ViewTypes, ScopeTemplates
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.shared.events import BootcampEvent, LoadEvent, LoadViewEvent

def getContextMenuHandlers():
    pass


def getViewSettings():
    from gui.Scaleform.daapi.view.bootcamp.BCOutroVideoPage import BCOutroVideoPage
    from gui.Scaleform.daapi.view.bootcamp.BCTooltipsWindow import BCTooltipsWindow
    from gui.Scaleform.daapi.view.bootcamp.BCHighlights import BCHighlights
    from gui.Scaleform.daapi.view.bootcamp.BCVehicleBuyView import BCVehicleBuyView
    from gui.Scaleform.daapi.view.bootcamp.BCQuestsView import BCQuestsView
    from gui.Scaleform.daapi.view.bootcamp.BCQueueDialog import BCQueueDialog
    return (ViewSettings(VIEW_ALIAS.BOOTCAMP_OUTRO_VIDEO, BCOutroVideoPage, 'BCOutroVideo.swf', ViewTypes.TOP_WINDOW, None, ScopeTemplates.TOP_WINDOW_SCOPE),
     ViewSettings(VIEW_ALIAS.BOOTCAMP_TOOLTIPS_WINDOW, BCTooltipsWindow, 'BCTooltipsWindow.swf', ViewTypes.WINDOW, None, ScopeTemplates.TOP_WINDOW_SCOPE),
     ViewSettings(VIEW_ALIAS.BOOTCAMP_LOBBY_HIGHLIGHTS, BCHighlights, 'BCHighlights.swf', ViewTypes.LOBBY_TOP_SUB, VIEW_ALIAS.BOOTCAMP_LOBBY_HIGHLIGHTS, ScopeTemplates.DEFAULT_SCOPE, True),
     ViewSettings(VIEW_ALIAS.BOOTCAMP_VEHICLE_BUY_VIEW, BCVehicleBuyView, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.BOOTCAMP_QUEUE_DIALOG, BCQueueDialog, 'BCQueueWindow.swf', ViewTypes.TOP_WINDOW, '', None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.BOOTCAMP_QUESTS_VIEW, BCQuestsView, 'BCQuestsView.swf', ViewTypes.LOBBY_TOP_SUB, None, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (BootcampPackageBusinessHandler(),)


class BootcampPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((VIEW_ALIAS.BOOTCAMP_LOBBY_OVERLAY_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.BOOTCAMP_INTRO_VIDEO, self.loadViewByCtxEvent),
         (VIEW_ALIAS.BOOTCAMP_OUTRO_VIDEO, self.loadViewByCtxEvent),
         (VIEW_ALIAS.BATTLE_RESULTS, self.loadViewByCtxEvent),
         (VIEW_ALIAS.BOOTCAMP_TOOLTIPS_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.LOBBY, self.loadViewByCtxEvent),
         (VIEW_ALIAS.BOOTCAMP_LOBBY_HIGHLIGHTS, self.loadViewByCtxEvent),
         (VIEW_ALIAS.LOBBY_RESEARCH, self.__loadResearch),
         (VIEW_ALIAS.LOBBY_TECHTREE, self.loadViewByCtxEvent),
         (VIEW_ALIAS.PERSONAL_CASE, self.loadViewByCtxEvent),
         (VIEW_ALIAS.VEHICLE_PREVIEW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.IMAGE_VIEW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.VEHICLE_PREVIEW_20, self.loadViewByCtxEvent),
         (VIEW_ALIAS.VEHICLE_BUY_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.FITTING_SELECT_POPOVER, self.loadViewByCtxEvent),
         (VIEW_ALIAS.PACK_ITEM_POPOVER, self.loadViewByCtxEvent),
         (VIEW_ALIAS.BOOTCAMP_QUESTS_VIEW, self.loadViewByCtxEvent),
         (LoadEvent.EXIT_FROM_RESEARCH, self.__exitFromResearch),
         (BootcampEvent.ADD_HIGHLIGHT, self.onShowHint),
         (BootcampEvent.REMOVE_HIGHLIGHT, self.onHideHint),
         (BootcampEvent.REMOVE_ALL_HIGHLIGHTS, self.onHideAllHints),
         (BootcampEvent.HINT_COMPLETE, self.onComplete),
         (BootcampEvent.HINT_HIDE, self.onHide),
         (BootcampEvent.HINT_CLOSE, self.onClose),
         (BootcampEvent.QUEUE_DIALOG_SHOW, self.queueDialogShow),
         (BootcampEvent.QUEUE_DIALOG_CLOSE, self.queueDialogClose))
        super(BootcampPackageBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
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

    def onBattleTypeSelectPopover(self, event):
        self.loadViewByCtxEvent(event)

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
        self.loadViewWithDefName(VIEW_ALIAS.LOBBY_RESEARCH, ctx=ctx)

    def __loadSimpleDialog(self, event):
        pass
