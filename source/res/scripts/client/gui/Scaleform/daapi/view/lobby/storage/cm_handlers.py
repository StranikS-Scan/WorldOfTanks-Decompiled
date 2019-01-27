# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/storage/cm_handlers.py
import inspect
from gui.Scaleform import MENU
from gui.Scaleform.framework.managers.context_menu import AbstractContextMenuHandler
_menuKey = MENU.cst_item_ctx_menu
CM_BUY_COLOR = 13347959

class CMLabel(object):
    INFORMATION = 'information'
    STATS = 'showVehicleStatistics'
    SELL = 'sell'
    REMOVE = 'remove'
    SALE_OPTION = 'saleOption'
    BUY = 'buy'
    BUY_MORE = 'buyMore'
    RENEW_RENT = 'rentRenew'
    ADD_TO_COMPARE = 'addToCompare'
    SHOW_IN_HANGAR = 'showInHangar'
    PREVIEW = 'preview'
    RESTORE = 'restore'
    ACTIVATE = 'activate'
    PREVIEW_CUSTOMIZATION = 'previewCustomization'


def option(order, label):

    def optionDecorator(method):

        def wrapper(self):
            method(self)

        wrapper.cm = {'order': order,
         'label': label,
         'name': method.__name__}
        return wrapper

    return optionDecorator


class ContextMenu(AbstractContextMenuHandler):

    def __init__(self, cmProxy=None, ctx=None):
        self.__handlerMethods = sorted([ method for method in (member.__func__ for _, member in inspect.getmembers(self, inspect.ismethod)) if getattr(method, 'cm', None) is not None ], key=lambda m: m.cm['order'])
        super(ContextMenu, self).__init__(cmProxy, ctx, {handler.cm['label']:handler.cm['name'] for handler in self.__handlerMethods})
        return

    def _initFlashValues(self, ctx):
        self._id = int(ctx.id)

    def _generateOptions(self, ctx=None):
        return [ self.__makeOption(method.cm['label'], self._getOptionCustomData(method.cm['label']) or {}) for method in self.__handlerMethods ]

    def __makeOption(self, label, data):
        return self._makeItem(label, _menuKey(data.pop('label', label)), data or None)

    def _getOptionCustomData(self, label):
        return None
