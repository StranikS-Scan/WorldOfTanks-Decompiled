# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/lobby/gui_lootboxes/__init__.py
import typing
if typing.TYPE_CHECKING:
    from gui.impl.pub import ViewImpl

class RegisteredTooltips(object):
    REGISTERED_SIMPLE_TOOLTIPS = {}
    REGISTERED_TOOLTIPS = {}

    @classmethod
    def registerLootBoxSimpleTooltipHandler(cls, tooltipResID, view):
        cls.REGISTERED_SIMPLE_TOOLTIPS[tooltipResID] = view

    @classmethod
    def registerLootBoxTooltipHandler(cls, tooltipResID, viewHandler):
        cls.REGISTERED_TOOLTIPS[tooltipResID] = viewHandler

    @classmethod
    def unregisterLootBoxTooltipHandler(cls, tooltipResID):
        if tooltipResID in cls.REGISTERED_TOOLTIPS:
            del cls.REGISTERED_TOOLTIPS[tooltipResID]
        if tooltipResID in cls.REGISTERED_SIMPLE_TOOLTIPS:
            del cls.REGISTERED_SIMPLE_TOOLTIPS[tooltipResID]


class LootBoxTooltipBaseHandler(object):

    def __init__(self, view):
        self.__view = view

    @property
    def view(self):
        return self.__view

    def __call__(self, event):
        raise NotImplementedError
