# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/comp7_event_banner.py
from account_helpers.AccountSettings import COMP7_BANNER_FIRST_APPEARANCE_TIMESTAMP
from comp7_core.gui.impl.lobby.event_banner import Comp7CoreEventBanner
from comp7.gui.impl.lobby.tooltips.entry_point_tooltip import Comp7EntryPointTooltip
from comp7.gui.impl.gen.view_models.views.lobby.season_model import SeasonState as Comp7SeasonState
from comp7.gui.comp7_constants import SELECTOR_BATTLE_TYPES, COMP7_ENTRY_POINT_ALIAS
from comp7.gui.prb_control.entities.comp7_prb_helpers import selectComp7
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller

class Comp7EventBanner(Comp7CoreEventBanner):
    NAME = COMP7_ENTRY_POINT_ALIAS
    __comp7Controller = dependency.descriptor(IComp7Controller)

    @property
    def _modeController(self):
        return self.__comp7Controller

    @property
    def _seasonStateClazz(self):
        return Comp7SeasonState

    @property
    def _accountSettingsTimestampFlag(self):
        return COMP7_BANNER_FIRST_APPEARANCE_TIMESTAMP

    @property
    def _selectorBattleType(self):
        return SELECTOR_BATTLE_TYPES.COMP7

    @staticmethod
    def _selectMode():
        selectComp7()

    @property
    def borderColor(self):
        pass

    @staticmethod
    @dependency.replace_none_kwargs(modeCtrl=IComp7Controller)
    def isEntryPointAvailable(modeCtrl=None):
        return modeCtrl.hasActiveSeason(includePreannounced=True)

    def createToolTipContent(self, event):
        super(Comp7EventBanner, self).createToolTipContent(event)
        return Comp7EntryPointTooltip()
