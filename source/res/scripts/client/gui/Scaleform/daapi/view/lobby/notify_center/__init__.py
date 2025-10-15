# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/notify_center/__init__.py
from debug_utils import LOG_WARNING
from frameworks.wulf import WindowLayer
from gui.Scaleform.framework import ScopeTemplates, ViewSettings, GroupedViewSettings
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.app_loader import settings as app_settings
from gui.shared import EVENT_BUS_SCOPE, events
from gui.notify_center import g_notifyCenterProvider

class NOTIFY_CENTER_ALIASES(object):
    MODAL_BASIC_WINDOW = 'notify_center/modalBasicWindow'
    NOT_MODAL_BASIC_WINDOW = 'notify_center/notModalBasicWindow'
    POLL_WINDOW = 'notify_center/pollWindow'
    SWF_DIALOG = 'NotifyCenterDialog.swf'
    UI_DIALOG = 'NotifyCenterDialog'


def getContextMenuHandlers():
    pass


def getViewSettings():
    from gui.Scaleform.daapi.view.lobby.notify_center.NotifyCenterDialog import NotifyCenterDialog
    return (ViewSettings(NOTIFY_CENTER_ALIASES.MODAL_BASIC_WINDOW, NotifyCenterDialog, NOTIFY_CENTER_ALIASES.SWF_DIALOG, WindowLayer.TOP_WINDOW, events.NotifyCenterShowItemEvent.SHOW_BASIC_WINDOW, ScopeTemplates.DEFAULT_SCOPE, isModal=True), GroupedViewSettings(NOTIFY_CENTER_ALIASES.NOT_MODAL_BASIC_WINDOW, NotifyCenterDialog, NOTIFY_CENTER_ALIASES.SWF_DIALOG, WindowLayer.WINDOW, NOTIFY_CENTER_ALIASES.UI_DIALOG, events.NotifyCenterShowItemEvent.SHOW_BASIC_WINDOW, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (_NotifyCenterPackageBusinessHandler(),)


class _NotifyCenterPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((events.NotifyCenterShowItemEvent.SHOW_BASIC_WINDOW, self.__showBasicWindow),)
        super(_NotifyCenterPackageBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)

    def __showBasicWindow(self, event):
        notID = event.getNotID()
        target = event.getTarget()
        item = g_notifyCenterProvider.getNotItemByName(notID, target)
        if not item:
            LOG_WARNING('Notification item is not found', notID, target)
            return
        else:
            if item.isModal():
                alias = NOTIFY_CENTER_ALIASES.MODAL_BASIC_WINDOW
            else:
                alias = NOTIFY_CENTER_ALIASES.NOT_MODAL_BASIC_WINDOW
            self.loadViewWithDefName(alias, '{0}_{1}'.format(NOTIFY_CENTER_ALIASES.MODAL_BASIC_WINDOW, notID), None, {'notID': notID,
             'target': target})
            return

    def __showPollWindow(self, event):
        notID = event.getNotID()
        target = event.getTarget()
        self.loadViewWithDefName(NOTIFY_CENTER_ALIASES.POLL_WINDOW, '{0}_{1}'.format(NOTIFY_CENTER_ALIASES.POLL_WINDOW, notID), None, {'notID': notID,
         'target': target})
        return
