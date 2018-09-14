# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/common/__init__.py
from gui.shared import EVENT_BUS_SCOPE
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import ViewSettings, GroupedViewSettings, ViewTypes, ScopeTemplates
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.shared.events import ShowDialogEvent

def getContextMenuHandlers():
    pass


def getViewSettings():
    from gui.Scaleform.daapi.view.common.report_bug import ReportBugPanel
    from gui.Scaleform.daapi.view.common.settings import SettingsWindow
    from gui.Scaleform.daapi.view.common.settings.acoustic_popover import AcousticPopover
    from gui.Scaleform.daapi.view.dialogs.SimpleDialog import SimpleDialog
    from gui.Scaleform.framework.WaitingView import WaitingView
    from gui.Scaleform.managers.Cursor import Cursor
    SETTINGS_WINDOW_SCOPE = ScopeTemplates.SimpleScope(VIEW_ALIAS.SETTINGS_WINDOW, ScopeTemplates.DEFAULT_SCOPE)
    return (ViewSettings(VIEW_ALIAS.CURSOR, Cursor, 'cursor.swf', ViewTypes.CURSOR, None, ScopeTemplates.GLOBAL_SCOPE),
     ViewSettings(VIEW_ALIAS.WAITING, WaitingView, 'waiting.swf', ViewTypes.WAITING, None, ScopeTemplates.GLOBAL_SCOPE),
     ViewSettings(VIEW_ALIAS.REPORT_BUG, ReportBugPanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.SIMPLE_DIALOG, SimpleDialog, 'simpleDialog.swf', ViewTypes.TOP_WINDOW, '', None, ScopeTemplates.DYNAMIC_SCOPE, isModal=True, canDrag=False),
     GroupedViewSettings(VIEW_ALIAS.SETTINGS_WINDOW, SettingsWindow, 'settingsWindow.swf', ViewTypes.TOP_WINDOW, 'settingsWindow', None, ScopeTemplates.DEFAULT_SCOPE, isModal=True, canDrag=False),
     GroupedViewSettings(VIEW_ALIAS.ACOUSTIC_POPOVER, AcousticPopover, 'acousticPopover.swf', ViewTypes.TOP_WINDOW, VIEW_ALIAS.ACOUSTIC_POPOVER, VIEW_ALIAS.ACOUSTIC_POPOVER, SETTINGS_WINDOW_SCOPE))


def getBusinessHandlers():
    return (CommonPackageBusinessHandler(), CommonDialogsHandler())


class CommonPackageBusinessHandler(PackageBusinessHandler):
    __slots__ = ()

    def __init__(self):
        listeners = ((VIEW_ALIAS.SETTINGS_WINDOW, self.loadViewByCtxEvent),)
        super(CommonPackageBusinessHandler, self).__init__(listeners, scope=EVENT_BUS_SCOPE.DEFAULT)


class CommonDialogsHandler(PackageBusinessHandler):
    __slots__ = ()

    def __init__(self):
        listeners = ((ShowDialogEvent.SHOW_SIMPLE_DLG, self.__loadSimpleDialog),)
        super(CommonDialogsHandler, self).__init__(listeners, scope=EVENT_BUS_SCOPE.GLOBAL)

    def __loadSimpleDialog(self, event):
        meta = event.meta
        self.loadViewWithGenName(VIEW_ALIAS.SIMPLE_DIALOG, meta.getMessage(), meta.getTitle(), meta.getButtonLabels(), meta.getCallbackWrapper(event.handler), meta.getViewScopeType(), meta.getTimer())
