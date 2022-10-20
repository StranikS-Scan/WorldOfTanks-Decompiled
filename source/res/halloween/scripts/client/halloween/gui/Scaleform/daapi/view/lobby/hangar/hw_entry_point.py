# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/Scaleform/daapi/view/lobby/hangar/hw_entry_point.py
from gui.Scaleform.daapi.view.meta.HW22EntryPointMeta import HW22EntryPointMeta
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.shared.system_factory import registerEntryPointValidator
from halloween.gui.impl.lobby.event_banner_view import EventBannerView
from halloween.skeletons.gui.game_event_controller import IHalloweenProgressController
from helpers import dependency
from skeletons.gui.game_control import IEventBattlesController

@dependency.replace_none_kwargs(eventCtrl=IEventBattlesController, hwProgressCtrl=IHalloweenProgressController)
def isHWEntryPointViewAvailable(eventCtrl=None, hwProgressCtrl=None):
    return eventCtrl.isEnabled() or hwProgressCtrl.isPostPhase()


@dependency.replace_none_kwargs(eventCtrl=IEventBattlesController, hwProgressCtrl=IHalloweenProgressController)
def canSelectPrbEntityFun(eventCtrl=None, hwProgressCtrl=None):
    return eventCtrl.isEnabled() and not hwProgressCtrl.isPostPhase()


def addHW22EntryPoint():
    registerEntryPointValidator(HANGAR_ALIASES.HW22_EVENT_ENTRY_POINT, isHWEntryPointViewAvailable)


class HW22EntryPoint(HW22EntryPointMeta):

    def _makeInjectView(self):
        self.__view = EventBannerView()
        return self.__view
