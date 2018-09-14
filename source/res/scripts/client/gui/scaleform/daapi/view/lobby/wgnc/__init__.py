# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/wgnc/__init__.py
from debug_utils import LOG_WARNING
from gui.Scaleform.framework import ScopeTemplates, ViewSettings, ViewTypes, GroupedViewSettings
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.app_loader.settings import APP_NAME_SPACE
from gui.shared import EVENT_BUS_SCOPE, events
from gui.wgnc import g_wgncProvider

class WGNC_ALIASES(object):
    MODAL_BASIC_WINDOW = 'wgnc/modalBasicWindow'
    NOT_MODAL_BASIC_WINDOW = 'wgnc/notModalBasicWindow'
    POLL_WINDOW = 'wgnc/pollWindow'
    SWF_DIALOG = 'WGNCDialog.swf'
    SWF_DIALOG_MODAL = 'WGNCDialogModal.swf'
    SWF_POLL_WINDOW = 'WGNCPollWindow.swf'
    UI_DIALOG = 'WGNCDialog'
    UI_POLL_WINDOW = 'WGNCPollWindowUI'


def getViewSettings():
    from gui.Scaleform.daapi.view.lobby.wgnc.WGNCDialog import WGNCDialog
    from gui.Scaleform.daapi.view.lobby.wgnc.WGNCPollWindow import WGNCPollWindow
    return (ViewSettings(WGNC_ALIASES.MODAL_BASIC_WINDOW, WGNCDialog, WGNC_ALIASES.SWF_DIALOG_MODAL, ViewTypes.TOP_WINDOW, events.WGNCShowItemEvent.SHOW_BASIC_WINDOW, ScopeTemplates.DEFAULT_SCOPE), GroupedViewSettings(WGNC_ALIASES.NOT_MODAL_BASIC_WINDOW, WGNCDialog, WGNC_ALIASES.SWF_DIALOG, ViewTypes.WINDOW, WGNC_ALIASES.UI_DIALOG, events.WGNCShowItemEvent.SHOW_BASIC_WINDOW, ScopeTemplates.DEFAULT_SCOPE), GroupedViewSettings(WGNC_ALIASES.POLL_WINDOW, WGNCPollWindow, WGNC_ALIASES.SWF_POLL_WINDOW, ViewTypes.WINDOW, WGNC_ALIASES.UI_POLL_WINDOW, events.WGNCShowItemEvent.SHOW_POLL_WINDOW, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (_WGNCPackageBusinessHandler(),)


class _WGNCPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((events.WGNCShowItemEvent.SHOW_BASIC_WINDOW, self.__showBasicWindow), (events.WGNCShowItemEvent.SHOW_POLL_WINDOW, self.__showPollWindow))
        super(_WGNCPackageBusinessHandler, self).__init__(listeners, APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)

    def __showBasicWindow(self, event):
        notID = event.getNotID()
        target = event.getTarget()
        item = g_wgncProvider.getNotItemByName(notID, target)
        if not item:
            LOG_WARNING('Notification item is not found', notID, target)
            return
        if item.isModal():
            alias = WGNC_ALIASES.MODAL_BASIC_WINDOW
        else:
            alias = WGNC_ALIASES.NOT_MODAL_BASIC_WINDOW
        self.loadViewWithDefName(alias, '{0}_{1}'.format(WGNC_ALIASES.MODAL_BASIC_WINDOW, notID), {'notID': notID,
         'target': target})

    def __showPollWindow(self, event):
        notID = event.getNotID()
        target = event.getTarget()
        self.loadViewWithDefName(WGNC_ALIASES.POLL_WINDOW, '{0}_{1}'.format(WGNC_ALIASES.POLL_WINDOW, notID), {'notID': notID,
         'target': target})
