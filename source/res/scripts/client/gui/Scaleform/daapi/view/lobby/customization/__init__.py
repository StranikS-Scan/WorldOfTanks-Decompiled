# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/__init__.py
from frameworks.wulf import WindowLayer
from gui.Scaleform.framework import GroupedViewSettings, ScopeTemplates, ViewSettings
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.Scaleform.genConsts.CUSTOMIZATION_ALIASES import CUSTOMIZATION_ALIASES
from gui.app_loader import settings as app_settings
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.events import ShowDialogEvent

def getContextMenuHandlers():
    from gui.impl.lobby.customization.widget.customization_cm_handlers import CustomizationItemCMHandler
    return ((CONTEXT_MENU_HANDLER_TYPE.CUSTOMIZATION_ITEM, CustomizationItemCMHandler),)


def getViewSettings():
    from gui.Scaleform.daapi.view.dialogs.confirm_customization_item_dialog import ConfirmCustomizationItemDialog
    return (GroupedViewSettings(CUSTOMIZATION_ALIASES.CONFIRM_CUSTOMIZATION_ITEM_DIALOG, ConfirmCustomizationItemDialog, 'confirmCustomizationItemDialog.swf', WindowLayer.TOP_WINDOW, 'confirmCustomizationItemDialog', None, ScopeTemplates.DEFAULT_SCOPE, isModal=True, canDrag=False),)


def getBusinessHandlers():
    return (CustomizationDialogPackageBusinessHandler(),)


class CustomizationDialogPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((ShowDialogEvent.SHOW_CONFIRM_C11N_BUY_DIALOG, self.__confirmCustomizationItemHandler), (ShowDialogEvent.SHOW_CONFIRM_C11N_SELL_DIALOG, self.__confirmCustomizationItemHandler))
        super(CustomizationDialogPackageBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.GLOBAL)

    def __confirmCustomizationItemHandler(self, event):
        self.loadViewWithGenName(CUSTOMIZATION_ALIASES.CONFIRM_CUSTOMIZATION_ITEM_DIALOG, None, event.meta, event.handler)
        return
