# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/views/new_year_info_view.py
from constants import CURRENT_REALM
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen.resources import R
from gui.impl.gen.view_models.views.lobby.new_year.views.new_year_info_view_model import NewYearInfoViewModel
from gui.impl.new_year.history_navigation import NewYearHistoryNavigation
from gui.shared.event_dispatcher import showNewYearInfoPage, showLootBoxBuyWindow, showLootBoxEntry, showLootBoxGuaranteedRewardsInfo, showLootBoxOpeningStream
from gui.shared.gui_items.loot_box import NewYearLootBoxes
from helpers import dependency, uniprof, getLanguageCode
from new_year.celebrity.celebrity_quests_helpers import getQuestCountForExtraSlot
from new_year.ny_bonuses import CreditsBonusHelper
from items.components.ny_constants import ToyTypes
from new_year.ny_constants import NyTabBarRewardsView, AnchorNames
from new_year.vehicle_branch import getInEventCooldown
from ny_common.settings import NYLootBoxConsts, NY_CONFIG_NAME
from ny_common.VehBranchConfig import BRANCH_SLOT_TYPE
from skeletons.gui.lobby_context import ILobbyContext
from uilogging.decorators import loggerTarget, loggerEntry, simpleLog
from uilogging.ny.constants import NY_LOG_KEYS
from uilogging.ny.loggers import NYLogger
_giftsOrder = (NewYearInfoViewModel.LEVELS,
 NewYearInfoViewModel.STYLES,
 NewYearInfoViewModel.SMALLBOXES,
 NewYearInfoViewModel.BIGBOXES)

@loggerTarget(logKey=NY_LOG_KEYS.NY_INFO_VIEW, loggerCls=NYLogger)
class NewYearInfoView(NewYearHistoryNavigation):
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, *args, **kwargs):
        super(NewYearInfoView, self).__init__(ViewSettings(R.views.lobby.new_year.InfoView(), flags=ViewFlags.VIEW, model=NewYearInfoViewModel()), *args, **kwargs)

    @loggerEntry
    def _onLoading(self, *args, **kwargs):
        super(NewYearInfoView, self)._onLoading()
        maxBonus = CreditsBonusHelper.getMaxBonus()
        maxMegaBonus = CreditsBonusHelper.getMegaToysBonusByCount(len(ToyTypes.MEGA))
        cooldowns = getInEventCooldown()
        with self.viewModel.transaction() as model:
            model.setMaxBonus(maxBonus)
            model.setUsualMaxBonus(maxBonus - maxMegaBonus)
            model.setSingleMegaBonus(CreditsBonusHelper.getMegaToysBonusValue())
            model.setMaxMegaBonus(maxMegaBonus)
            model.setRegularSlotCooldownValue(cooldowns[BRANCH_SLOT_TYPE.REGULAR])
            model.setExtraSlotCooldownValue(cooldowns[BRANCH_SLOT_TYPE.EXTRA])
            model.setRealm(CURRENT_REALM)
            model.setLanguage(getLanguageCode())
            model.setQuestsToGetExtraSlot(getQuestCountForExtraSlot())
            self.__updateStatus(model)

    @uniprof.regionDecorator(label='ny.info', scope='enter')
    def _initialize(self, *args, **kwargs):
        super(NewYearInfoView, self)._initialize()
        self.viewModel.onVideoClicked += self.__onVideoClicked
        self.viewModel.onButtonClick += self.__onButtonClick
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged

    @uniprof.regionDecorator(label='ny.info', scope='exit')
    def _finalize(self):
        self.viewModel.onVideoClicked -= self.__onVideoClicked
        self.viewModel.onButtonClick -= self.__onButtonClick
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
        super(NewYearInfoView, self)._finalize()

    @property
    def viewModel(self):
        return super(NewYearInfoView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        pass

    def __updateStatus(self, model):
        isLootBoxesEnabled = self.__lobbyContext.getServerSettings().isLootBoxesEnabled()
        isExternalBuyBox = self.__lobbyContext.getServerSettings().getLootBoxShop().get(NYLootBoxConsts.SOURCE, NYLootBoxConsts.EXTERNAL) == NYLootBoxConsts.EXTERNAL
        model.setIsExternalBuyBox(isExternalBuyBox)
        model.setIsLootBoxEnabled(isLootBoxesEnabled)

    @simpleLog(argsIndex=0, preProcessAction=lambda x: x['value'])
    def __onButtonClick(self, args):
        action = args['value']
        if action == NewYearInfoViewModel.LEVELS:
            self._goToRewardsView(tabName=NyTabBarRewardsView.FOR_LEVELS)
        elif action == NewYearInfoViewModel.STYLES:
            self._goToRewardsView(tabName=NyTabBarRewardsView.COLLECTION_NY21)
        elif action == NewYearInfoViewModel.BIGBOXES:
            showLootBoxBuyWindow()
        elif action == NewYearInfoViewModel.SMALLBOXES:
            showLootBoxEntry(lootBoxType=NewYearLootBoxes.COMMON)
        elif action == NewYearInfoViewModel.CELEBRITY:
            self.switchByAnchorName(AnchorNames.CELEBRITY)
        elif action == NewYearInfoViewModel.GUARANTEED_REWARDS:
            showLootBoxGuaranteedRewardsInfo()
        elif action == NewYearInfoViewModel.STREAM_BOX:
            showLootBoxOpeningStream()

    @staticmethod
    def __onVideoClicked():
        showNewYearInfoPage()

    def __onServerSettingsChanged(self, diff):
        if 'isLootBoxesEnabled' in diff or diff.get(NY_CONFIG_NAME, {}).get(NYLootBoxConsts.CONFIG_NAME) is not None:
            self.__updateStatus(self.viewModel)
        return
