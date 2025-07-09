# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/frontline/__init__.py
import typing
if typing.TYPE_CHECKING:
    from gui.impl.pub import ViewImpl

class RegisteredFrontlineTooltips(object):
    REGISTERED_SIMPLE_TOOLTIPS = {}
    REGISTERED_TOOLTIPS = {}

    @classmethod
    def registerFrontlineSimpleTooltipHandler(cls, tooltipResID, view):
        cls.REGISTERED_SIMPLE_TOOLTIPS[tooltipResID] = view

    @classmethod
    def registerFrontlineTooltipHandler(cls, tooltipResID, viewHandler):
        cls.REGISTERED_TOOLTIPS[tooltipResID] = viewHandler

    @classmethod
    def unregisterFrontlineTooltipHandler(cls, tooltipResID):
        if tooltipResID in cls.REGISTERED_TOOLTIPS:
            del cls.REGISTERED_TOOLTIPS[tooltipResID]
        if tooltipResID in cls.REGISTERED_SIMPLE_TOOLTIPS:
            del cls.REGISTERED_SIMPLE_TOOLTIPS[tooltipResID]


class FrontlineTooltipBaseHandler(object):

    def __init__(self, view):
        self.__view = view

    @property
    def view(self):
        return self.__view

    def __call__(self, event):
        raise NotImplementedError
