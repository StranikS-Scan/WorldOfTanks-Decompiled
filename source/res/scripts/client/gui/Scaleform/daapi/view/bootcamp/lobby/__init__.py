# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/lobby/__init__.py
from bootcamp.Bootcamp import g_bootcamp
from frameworks.wulf import WindowLayer
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.app_loader import settings as app_settings
from gui.shared import EVENT_BUS_SCOPE
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import ViewSettings, GroupedViewSettings, ScopeTemplates, ComponentSettings
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.shared.events import LoadViewEvent

def getContextMenuHandlers():
    pass


def getViewSettings():
    from gui.Scaleform.daapi.view.bootcamp.BCOutroVideoPage import BCOutroVideoPage
    from gui.Scaleform.daapi.view.bootcamp.BCTooltipsWindow import BCTooltipsWindow
    from gui.Scaleform.daapi.view.bootcamp.BCHighlights import BCHighlights
    from gui.Scaleform.daapi.view.bootcamp.BCVehicleBuyView import BCVehicleBuyView
    from gui.Scaleform.daapi.view.bootcamp.BCQuestsView import BCQuestsView
    from gui.Scaleform.daapi.view.bootcamp.BCQueueDialog import BCQueueDialog
    from gui.Scaleform.daapi.view.bootcamp.BCSubtitlesWindow import SubtitlesWindow
    from gui.Scaleform.daapi.view.bootcamp.BCInterludeVideoPage import BCInterludeVideoPage
    return (ViewSettings(VIEW_ALIAS.BOOTCAMP_OUTRO_VIDEO, BCOutroVideoPage, 'BCOutroVideo.swf', WindowLayer.TOP_WINDOW, VIEW_ALIAS.BOOTCAMP_OUTRO_VIDEO, ScopeTemplates.TOP_WINDOW_SCOPE, canClose=False, canDrag=True),
     ViewSettings(VIEW_ALIAS.BOOTCAMP_TOOLTIPS_WINDOW, BCTooltipsWindow, 'BCTooltipsWindow.swf', WindowLayer.WINDOW, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.BOOTCAMP_LOBBY_HIGHLIGHTS, BCHighlights, 'BCHighlights.swf', WindowLayer.TOP_SUB_VIEW, VIEW_ALIAS.BOOTCAMP_LOBBY_HIGHLIGHTS, ScopeTemplates.DEFAULT_SCOPE, True),
     ComponentSettings(VIEW_ALIAS.BOOTCAMP_VEHICLE_BUY_VIEW, BCVehicleBuyView, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.BOOTCAMP_QUEUE_DIALOG, BCQueueDialog, 'BCQueueWindow.swf', WindowLayer.TOP_WINDOW, '', None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.BOOTCAMP_QUESTS_VIEW, BCQuestsView, 'missionsDetails.swf', WindowLayer.TOP_SUB_VIEW, VIEW_ALIAS.BOOTCAMP_QUESTS_VIEW, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.SUBTITLES_WINDOW, SubtitlesWindow, 'SubtitlesWindow.swf', WindowLayer.OVERLAY, VIEW_ALIAS.SUBTITLES_WINDOW, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.BOOTCAMP_INTERLUDE_VIDEO, BCInterludeVideoPage, 'BCOutroVideo.swf', WindowLayer.TOP_WINDOW, VIEW_ALIAS.BOOTCAMP_INTERLUDE_VIDEO, ScopeTemplates.TOP_WINDOW_SCOPE, canClose=False, canDrag=True))


def getBusinessHandlers():
    return (BootcampPackageBusinessHandler(),)


class BootcampPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((VIEW_ALIAS.BOOTCAMP_OUTRO_VIDEO, self.loadViewByCtxEvent),
         (VIEW_ALIAS.BOOTCAMP_TOOLTIPS_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.BOOTCAMP_LOBBY_HIGHLIGHTS, self.loadViewByCtxEvent),
         (VIEW_ALIAS.BOOTCAMP_MESSAGE_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.BOOTCAMP_INTERLUDE_VIDEO, self.loadViewByCtxEvent),
         (VIEW_ALIAS.BOOTCAMP_QUESTS_VIEW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.SUBTITLES_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.BOOTCAMP_ADD_HIGHLIGHT, self.__onShowHint),
         (VIEW_ALIAS.BOOTCAMP_REMOVE_HIGHLIGHT, self.__onHideHint),
         (VIEW_ALIAS.BOOTCAMP_HINT_COMPLETE, self.__onComplete),
         (VIEW_ALIAS.BOOTCAMP_HINT_HIDE, self.__onHide),
         (VIEW_ALIAS.BOOTCAMP_HINT_CLOSE, self.__onClose),
         (VIEW_ALIAS.BOOTCAMP_QUEUE_DIALOG_SHOW, self.__queueDialogShow),
         (VIEW_ALIAS.BOOTCAMP_QUEUE_DIALOG_CLOSE, self.__queueDialogClose))
        super(BootcampPackageBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)

    def __onHideHint(self, event):
        hintWindow = self.findViewByAlias(WindowLayer.TOP_SUB_VIEW, VIEW_ALIAS.BOOTCAMP_LOBBY_HIGHLIGHTS)
        if hintWindow is not None:
            hintWindow.hideHint(event.ctx)
        return

    def __onShowHint(self, event):
        hintWindow = self.findViewByAlias(WindowLayer.TOP_SUB_VIEW, VIEW_ALIAS.BOOTCAMP_LOBBY_HIGHLIGHTS)
        if hintWindow is not None:
            hintWindow.showHint(event.ctx)
        return

    def __onHide(self, _):
        hintWindow = self.findViewByAlias(WindowLayer.WINDOW, VIEW_ALIAS.BOOTCAMP_TOOLTIPS_WINDOW)
        if hintWindow is not None:
            hintWindow.as_hideHandlerS()
        return

    def __onComplete(self, _):
        hintWindow = self.findViewByAlias(WindowLayer.WINDOW, VIEW_ALIAS.BOOTCAMP_TOOLTIPS_WINDOW)
        if hintWindow is not None:
            hintWindow.as_completeHandlerS()
        return

    def __onClose(self, _):
        hintWindow = self.findViewByAlias(WindowLayer.WINDOW, VIEW_ALIAS.BOOTCAMP_TOOLTIPS_WINDOW)
        if hintWindow is not None:
            hintWindow.destroy()
        return

    def __queueDialogShow(self, _):
        ctx = {'backgroundImage': '../maps/login/back_25_without_sparks.png',
         'lessonNumber': g_bootcamp.getLessonNum(),
         'timeout': g_bootcamp.getContextIntParameter('lessonQueueTimeout', 15)}
        queueDialog = self.findViewByAlias(WindowLayer.TOP_WINDOW, VIEW_ALIAS.BOOTCAMP_QUEUE_DIALOG)
        if queueDialog:
            queueDialog.updateSettings(ctx)
            return
        self.loadViewByCtxEvent(LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.BOOTCAMP_QUEUE_DIALOG), ctx=ctx))

    def __queueDialogClose(self, _):
        queueDialog = self.findViewByAlias(WindowLayer.TOP_WINDOW, VIEW_ALIAS.BOOTCAMP_QUEUE_DIALOG)
        if queueDialog:
            queueDialog.destroy()
