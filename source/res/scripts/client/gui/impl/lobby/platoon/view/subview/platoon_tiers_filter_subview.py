# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/platoon/view/subview/platoon_tiers_filter_subview.py
import logging
from account_helpers.settings_core.settings_constants import GAME
from gui.impl.gen.view_models.views.lobby.platoon.settings_model import SettingsModel, SearchFilterTypes
from gui.impl.gen.view_models.views.lobby.platoon.tier_button_model import TierButtonModel
from UnitBase import UnitAssemblerSearchFlags, BitfieldHelper
from helpers import dependency
from gui.impl.gen import R
from skeletons.gui.game_control import IPlatoonController
from skeletons.gui.shared import IItemsCache
from frameworks.wulf.view.view_model import ViewModel
from skeletons.gui.lobby_context import ILobbyContext
from gui.impl.pub.view_impl import ViewImpl, PopOverViewImpl
from frameworks.wulf import ViewSettings
from skeletons.account_helpers.settings_core import ISettingsCore
_logger = logging.getLogger(__name__)

class TiersFilterSubview(ViewImpl):
    __platoonCtrl = dependency.descriptor(IPlatoonController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __settingsCore = dependency.descriptor(ISettingsCore)
    MIN_LEVEL = 1
    MAX_LEVEL = 10

    def __init__(self):
        settings = ViewSettings(layoutID=R.views.lobby.platoon.subViews.SettingsContent(), model=SettingsModel())
        self.__unitFilter = None
        super(TiersFilterSubview, self).__init__(settings)
        return

    def update(self, *args):
        with self.viewModel.transaction() as model:
            filterTypesArray = model.getSearchFilterTypes()
            filterTypesArray.clear()
            if self.__platoonCtrl.isTankLevelPreferenceEnabled():
                filterTypesArray.addString(SearchFilterTypes.TIER.value)
                self.__updateTierSettings()
            if self.__platoonCtrl.isVOIPEnabled():
                filterTypesArray.addString(SearchFilterTypes.VOICE.value)
                self.__updateVoiceChat()
            filterTypesArray.invalidate()

    @property
    def viewModel(self):
        return self.getViewModel()

    def _finalize(self):
        self.__removeListeners()

    def _onLoading(self, *args, **kwargs):
        self.__addListeners()
        self.update()

    def __updateTierSettings(self):
        self.__unitFilter = BitfieldHelper(self.__platoonCtrl.getUnitFilter())
        with self.viewModel.transaction() as model:
            tierArray = model.tiersSettings.getTierButtons()
            tierArray.clear()
            for index in range(self.MIN_LEVEL, self.MAX_LEVEL + 1):
                self.__addTierButton(tierArray, index)

            tierArray.invalidate()
            self.__platoonCtrl.saveUnitFilter(self.__unitFilter.value)

    def __addListeners(self):
        with self.viewModel.transaction() as model:
            model.tiersSettings.onSwitchTier += self.__onSwitchTier
            model.voiceSettings.switchVoiceChat += self.__onSwitchVoiceChat
        self.__settingsCore.onSettingsChanged += self.__onSettingsChanged

    def __removeListeners(self):
        with self.viewModel.transaction() as model:
            model.tiersSettings.onSwitchTier -= self.__onSwitchTier
            model.voiceSettings.switchVoiceChat -= self.__onSwitchVoiceChat
        self.__settingsCore.onSettingsChanged -= self.__onSettingsChanged

    def __onSettingsChanged(self, diff):
        if GAME.UNIT_FILTER in diff:
            self.update()

    def __updateVoiceChat(self):
        self.__unitFilter = BitfieldHelper(self.__platoonCtrl.getUnitFilter())
        enableVoiceChat = self.__unitFilter.isSetFlag(UnitAssemblerSearchFlags.USE_VOICE)
        with self.viewModel.transaction() as model:
            model.voiceSettings.setIsVoiceChatEnabled(enableVoiceChat)

    def __addTierButton(self, tierArray, tier):
        tierButtonModel = TierButtonModel()
        isTierEnabled = self.__isTierEnabled(tier)
        tierButtonModel.setIsEnabled(isTierEnabled)
        if not isTierEnabled:
            self.__unitFilter.unsetBit(tier)
        tierButtonModel.setIsSelected(self.__unitFilter.isSetBit(tier) and isTierEnabled)
        tierButtonModel.setTier(tier)
        tierArray.addViewModel(tierButtonModel)

    def __isTierEnabled(self, tier):
        return self.__platoonCtrl.hasVehiclesForSearch(tierLevel=tier)

    def __onSwitchTier(self, *args, **kwargs):
        if args:
            if args[0]['tier'] is not None:
                tier = int(args[0]['tier'])
                self.__unitFilter.toggleBit(tier)
                self.__platoonCtrl.saveUnitFilter(self.__unitFilter.value)
                self.__updateTierSettings()
        return

    def __onSwitchVoiceChat(self):
        self.__unitFilter = BitfieldHelper(self.__platoonCtrl.getUnitFilter())
        self.__unitFilter.toggleFlag(UnitAssemblerSearchFlags.USE_VOICE)
        self.__platoonCtrl.saveUnitFilter(self.__unitFilter.value)
        self.__updateVoiceChat()


class SettingsPopover(PopOverViewImpl):

    def __init__(self):
        settings = ViewSettings(layoutID=R.views.lobby.platoon.SettingsPopover(), model=ViewModel())
        super(SettingsPopover, self).__init__(settings)

    def _onLoading(self, *args, **kwargs):
        tiersFilterSubview = TiersFilterSubview()
        self.setChildView(tiersFilterSubview.layoutID, tiersFilterSubview)
