# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/impl/lobby/comp7_light_event_banner.py
from gui.impl import backport
from gui.impl.gen import R
from account_helpers.AccountSettings import COMP7_LIGHT_BANNER_FIRST_APPEARANCE_TIMESTAMP
from comp7_core.gui.impl.lobby.event_banner import Comp7CoreEventBanner
from comp7_light.gui.comp7_light_constants import SELECTOR_BATTLE_TYPES, COMP7_LIGHT_ENTRY_POINT_ALIAS
from comp7_light.gui.impl.gen.view_models.views.lobby.season_model import SeasonState as Comp7LightSeasonState
from comp7_light.gui.impl.lobby.tooltips.entry_point_tooltip import Comp7LightEntryPointTooltip
from comp7_light.gui.prb_control.entities.comp7_light_prb_helpers import selectComp7Light
from helpers import dependency
from skeletons.gui.game_control import IComp7LightController

class Comp7LightEventBanner(Comp7CoreEventBanner):
    NAME = COMP7_LIGHT_ENTRY_POINT_ALIAS
    __comp7LightController = dependency.descriptor(IComp7LightController)

    @property
    def _modeController(self):
        return self.__comp7LightController

    @property
    def _seasonStateClazz(self):
        return Comp7LightSeasonState

    @property
    def _accountSettingsTimestampFlag(self):
        return COMP7_LIGHT_BANNER_FIRST_APPEARANCE_TIMESTAMP

    @property
    def _selectorBattleType(self):
        return SELECTOR_BATTLE_TYPES.COMP7_LIGHT

    @staticmethod
    def _selectMode():
        selectComp7Light()

    @property
    def introDescription(self):
        return backport.text(R.strings.hangar_event_banners.event.Comp7LightEntryPoint.intro.description(), level=self._vehicleLevel)

    @property
    def inProgressDescription(self):
        return backport.text(R.strings.hangar_event_banners.event.Comp7LightEntryPoint.inProgress.description(), level=self._vehicleLevel)

    @property
    def borderColor(self):
        pass

    @staticmethod
    @dependency.replace_none_kwargs(modeCtrl=IComp7LightController)
    def isEntryPointAvailable(modeCtrl=None):
        return modeCtrl.hasActiveSeason()

    def createToolTipContent(self, event):
        super(Comp7LightEventBanner, self).createToolTipContent(event)
        return Comp7LightEntryPointTooltip()
