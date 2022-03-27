# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/shared/cm_handlers.py
import inspect
from gui.Scaleform.framework.managers.context_menu import AbstractContextMenuHandler
from gui.impl import backport
from gui.impl.gen import R

def _makeMenuLabel(label, data):
    return backport.text(R.strings.menu.cst_item_ctx_menu.dyn(data.pop('label', label))(), **data.pop('labelCtx', {}))


class CMLabel(object):
    INFORMATION = 'information'
    STATS = 'showVehicleStatistics'
    SELL = 'sell'
    REMOVE = 'remove'
    SALE_OPTION = 'saleOption'
    BUY = 'buy'
    BUY_MORE = 'buyMore'
    EXCHANGE = 'exchange'
    ADD_TO_COMPARE = 'addToCompare'
    SHOW_IN_HANGAR = 'showInHangar'
    PREVIEW = 'preview'
    RESTORE = 'restore'
    ACTIVATE = 'activate'
    PREVIEW_CUSTOMIZATION = 'previewCustomization'
    CONVERT_BLUEPRINT = 'convertBlueprint'
    CONVERT_BLUEPRINT_MAX = 'convertBlueprintMax'
    SHOW_BLUEPRINT = 'showBlueprint'
    NATION_CHANGE = 'nationChange'
    UPGRADE = 'upgrade'
    GO_TO_COLLECTION = 'goToCollection'


def option(order, label):

    def optionDecorator(method):

        def wrapper(self):
            method(self)

        wrapper.cm = {'order': order,
         'label': label,
         'name': method.__name__}
        return wrapper

    return optionDecorator


class StorageOptionCustomData(object):

    def __init__(self, label, enabled=True, visible=True, isNew=False, textColor=None, labelCtx=None):
        self.label = label
        self.enabled = enabled
        self.visible = visible
        self.isNew = isNew
        self.textColor = textColor
        self.labelCtx = labelCtx

    def asDict(self):
        return {key:value for key, value in inspect.getmembers(self, lambda m: not inspect.ismethod(m)) if not (key.startswith('_') or key.startswith('__')) and value is not None}


class ContextMenu(AbstractContextMenuHandler):

    def __init__(self, cmProxy=None, ctx=None):
        self.__handlerMethods = sorted([ method for method in (member.__func__ for _, member in inspect.getmembers(self, inspect.ismethod)) if getattr(method, 'cm', None) is not None ], key=lambda m: m.cm['order'])
        super(ContextMenu, self).__init__(cmProxy, ctx, {handler.cm['label']:handler.cm['name'] for handler in self.__handlerMethods})
        return

    def _initFlashValues(self, ctx):
        self._id = int(ctx.id)

    def _generateOptions(self, ctx=None):
        return [ self._makeOption(method.cm['label'], self._getOptionCustomData(method.cm['label']).asDict()) for method in self.__handlerMethods if self._isVisible(method.cm['label']) ]

    def _makeOption(self, label, data):
        return self._makeItem(optId=label, optLabel=_makeMenuLabel(label, data), optInitData=data or None)

    def _getOptionCustomData(self, label):
        return StorageOptionCustomData(label)

    def _isVisible(self, label):
        return True
