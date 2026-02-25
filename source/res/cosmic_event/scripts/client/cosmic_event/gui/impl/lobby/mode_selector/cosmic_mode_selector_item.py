# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/impl/lobby/mode_selector/cosmic_mode_selector_item.py
from enum import Enum
from frameworks.wulf import WindowLayer
from gui import GUI_SETTINGS
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_normal_card_model import BattlePassState
from gui.impl.lobby.mode_selector.items.base_item import ModeSelectorLegacyItem, formatSeasonLeftTime
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_cosmic_model import ModeSelectorCosmicModel
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_card_types import ModeSelectorCardTypes
from gui.impl.lobby.mode_selector.items.items_constants import ModeSelectorRewardID
from skeletons.gui.game_control import ICosmicEventBattleController
from gui.shared.event_dispatcher import showBrowserOverlayView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from helpers import dependency, time_utils
from cosmic_account_settings import isCosmicBattlePassShown, setCosmicBattlePassShown
from cosmic_event.skeletons.progression_controller import ICosmicEventProgressionController

class _CosmicModeSelectorRewardID(Enum):
    EXPERIMENTAL_EQUIPMENT = 'experimentalEquipment'


class CosmicEventModeSelectorItem(ModeSelectorLegacyItem):
    __slots__ = ()
    _VIEW_MODEL = ModeSelectorCosmicModel
    _CARD_VISUAL_TYPE = ModeSelectorCardTypes.COSMIC
    _cosmicEventBattleCtrl = dependency.descriptor(ICosmicEventBattleController)
    _cosmicProgression = dependency.descriptor(ICosmicEventProgressionController)

    @property
    def viewModel(self):
        return self._viewModel

    @property
    def isSelectable(self):
        return self._cosmicEventBattleCtrl.isEnabled

    @property
    def isSuspended(self):
        return self._cosmicEventBattleCtrl.isTemporaryUnavailable()

    def _isInfoIconVisible(self):
        return True

    def handleInfoPageClick(self):
        url = self._getInfoPageURL()
        showBrowserOverlayView(url, VIEW_ALIAS.WEB_VIEW_TRANSPARENT, hiddenLayers=(WindowLayer.MARKER, WindowLayer.VIEW, WindowLayer.WINDOW))

    def _onInitializing(self):
        super(CosmicEventModeSelectorItem, self)._onInitializing()
        self.__setData()
        self.viewModel.setName(backport.text(R.strings.mode_selector.mode.cosmic_event.title()))
        if self._cosmicEventBattleCtrl.isBattleAvailable():
            self._addReward(_CosmicModeSelectorRewardID.EXPERIMENTAL_EQUIPMENT)
            self._addReward(ModeSelectorRewardID.LOOTBOX)
            if not isCosmicBattlePassShown():
                state = BattlePassState.NEW
                setCosmicBattlePassShown(True)
            else:
                state = BattlePassState.STATIC
            self.viewModel.setBattlePassState(state)

    def _getInfoPageURL(self):
        return GUI_SETTINGS.cosmicInfoPageURL

    def __setData(self):
        with self.viewModel.transaction() as model:
            if self._cosmicEventBattleCtrl.isAvailable():
                model.setTimeLeft(formatSeasonLeftTime(self._cosmicEventBattleCtrl.getCurrentSeason()))
            self.__fillWidget(model.widget)
            self.__updateSuspendedStatus(model)

    def __onUpdated(self, *_):
        self.__setData()

    def __fillWidget(self, model):
        ctrl = self._cosmicEventBattleCtrl
        model.setIsEnabled(ctrl.isEnabled)
        model.setCurrentProgress(self._cosmicProgression.getCurrentPoints())
        model.setTotalCount(self._cosmicProgression.getMaxProgressionPoints())

    def __updateSuspendedStatus(self, model):
        model.setIsSuspended(self.isSuspended)

    def __getCurrentSeasonDates(self):
        currentSeason = self._cosmicEventBattleCtrl.getCurrentSeason()
        if currentSeason is None:
            return 0
        else:
            periodInfo = self._cosmicEventBattleCtrl.getPeriodInfo()
            daysLeft = periodInfo.cycleBorderRight.delta(periodInfo.now) / time_utils.ONE_DAY
            return max(0, daysLeft)

    @property
    def calendarTooltipText(self):
        daysLeft = int(self.__getCurrentSeasonDates() or 0)
        return backport.ntext(R.strings.mode_selector.cosmic_event.calendarTooltip.body(), daysLeft, days=daysLeft)
