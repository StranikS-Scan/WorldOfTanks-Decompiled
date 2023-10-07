# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/Scaleform/daapi/view/lobby/hangar/hw_entry_point.py
from gui.Scaleform.daapi.view.meta.HW22EntryPointMeta import HW22EntryPointMeta
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.shared.system_factory import registerBannerEntryPointValidator, registerBannerEntryPointLUIRule
from halloween.gui.impl.lobby.event_banner_view import EventBannerView
from gui.limited_ui.lui_rules_storage import LuiRules
from helpers import dependency
from skeletons.gui.game_control import IHalloweenController

@dependency.replace_none_kwargs(eventCtrl=IHalloweenController)
def isHWEntryPointViewAvailable(eventCtrl=None):
    return eventCtrl.isEnabled() or eventCtrl.isPostPhase()


@dependency.replace_none_kwargs(eventCtrl=IHalloweenController)
def canSelectPrbEntityFun(eventCtrl=None):
    return eventCtrl.isEnabled() and not eventCtrl.isPostPhase()


def addHW22EntryPoint():
    registerBannerEntryPointValidator(HANGAR_ALIASES.HW22_EVENT_ENTRY_POINT, isHWEntryPointViewAvailable)
    registerBannerEntryPointLUIRule(HANGAR_ALIASES.HW22_EVENT_ENTRY_POINT, LuiRules.GUI_HALLOWEEN_ENTRY_POINT)


class HW22EntryPoint(HW22EntryPointMeta):

    def _makeInjectView(self):
        self.__view = EventBannerView()
        return self.__view
