# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/__init__.py
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.View import ViewKey
from gui.Scaleform.framework.managers.view_lifecycle_watcher import IViewLifecycleHandler

class DiscountPopoverHandler(IViewLifecycleHandler):

    def __init__(self, onViewCreatedCallback, onViewDestroyedCallback):
        super(DiscountPopoverHandler, self).__init__([ViewKey(VIEW_ALIAS.NY_SELECT_VEHICLE_FOR_DISCOUNT_POPOVER)])
        self.__onViewCreatedCallback = onViewCreatedCallback
        self.__onViewDestroyedCallback = onViewDestroyedCallback

    def onViewCreated(self, view):
        self.__onViewCreatedCallback()

    def onViewDestroyed(self, _):
        self.__onViewDestroyedCallback()
