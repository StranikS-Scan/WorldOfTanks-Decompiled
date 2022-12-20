# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/Scaleform/daapi/view/lobby/hangar/entry_point.py
from helpers import dependency
from entry_point_view import EpicBattlesEntryPointView
from frameworks.wulf import ViewFlags
from gui.Scaleform.daapi.view.meta.EpicBattlesEntryPointMeta import EpicBattlesEntryPointMeta
from gui.Scaleform.genConsts.EPICBATTLES_ALIASES import EPICBATTLES_ALIASES
from gui.periodic_battles.models import PrimeTimeStatus
from gui.shared.system_factory import registerEntryPointValidator
from skeletons.gui.game_control import IEpicBattleMetaGameController

@dependency.replace_none_kwargs(epicController=IEpicBattleMetaGameController)
def isEpicBattlesEntryPointAvailable(epicController=None):
    from frontline.gui.frontline_helpers import geFrontlineState
    from frontline.gui.impl.gen.view_models.views.lobby.views.frontline_const import FrontlineState
    state, _, _ = geFrontlineState()
    primeTimeStatus, _, _ = epicController.getPrimeTimeStatus()
    hasUnclaimedRewards = epicController.getNotChosenRewardCount()
    return False if not epicController.isEnabled() or not epicController.getCurrentSeasonID() or primeTimeStatus in [PrimeTimeStatus.NOT_SET, PrimeTimeStatus.FROZEN] or state == FrontlineState.FINISHED and not hasUnclaimedRewards else True


def addFrontlineEntryPoint():
    registerEntryPointValidator(EPICBATTLES_ALIASES.EPIC_BATTLES_ENTRY_POINT, isEpicBattlesEntryPointAvailable)


class EpicBattlesEntryPoint(EpicBattlesEntryPointMeta):

    def _makeInjectView(self):
        self.__view = EpicBattlesEntryPointView(flags=ViewFlags.COMPONENT)
        return self.__view
