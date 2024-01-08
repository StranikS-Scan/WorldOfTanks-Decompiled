# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/lobby/views/awards_view.py
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer
from gui.battle_pass.battle_pass_decorators import createBackportTooltipDecorator, createTooltipContentDecorator
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.common.awards_view_model import AwardsViewModel
from gui.impl.gen.view_models.views.lobby.common.reward_item_model import RewardItemModel
from gui.impl.gui_decorators import args2params
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.server_events.bonuses import getNonQuestBonuses, mergeBonuses, splitBonuses
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.missions.packers.bonus import ItemBonusUIPacker, BonusUIPacker, getDefaultBonusPackersMap
from helpers import dependency
from skeletons.gui.game_control import IEpicBattleMetaGameController
from uilogging.epic_battle.constants import EpicBattleLogKeys, EpicBattleLogButtons, EpicBattleLogActions
from uilogging.epic_battle.loggers import EpicBattleTooltipLogger
MAIN_REWARDS_LIMIT = 4

class AwardsView(ViewImpl):
    __slots__ = ('__tooltipItems', '__onCloseCallback', '__onAnimationEndedCallback', '__isAnimationEnded', '__uiEpicBattleLogger')

    def __init__(self, bonuses, onCloseCallback=None, onAnimationEnded=None):
        settings = ViewSettings(R.views.lobby.common.AwardsView())
        settings.model = AwardsViewModel()
        settings.kwargs = {'bonuses': bonuses}
        super(AwardsView, self).__init__(settings)
        self.__isAnimationEnded = False
        self.__tooltipItems = {}
        self.__onCloseCallback = onCloseCallback
        self.__onAnimationEndedCallback = onAnimationEnded
        self.__uiEpicBattleLogger = EpicBattleTooltipLogger()

    @property
    def viewModel(self):
        return super(AwardsView, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(AwardsView, self).createToolTip(event)

    @createTooltipContentDecorator()
    def createToolTipContent(self, event, contentID):
        return None

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltipItems.get(tooltipId)

    def _initialize(self, *args, **kwargs):
        super(AwardsView, self)._initialize(*args, **kwargs)
        self.__uiEpicBattleLogger.initialize(EpicBattleLogKeys.AWARDS_VIEW.value)

    def _finalize(self):
        super(AwardsView, self)._finalize()
        self.__uiEpicBattleLogger.reset()
        self.__safeCall(self.__onCloseCallback)

    def _onLoading(self, bonuses, *args, **kwargs):
        super(AwardsView, self)._onLoading(*args, **kwargs)
        rewards = composeBonuses(bonuses)
        if not rewards:
            return
        locales = R.strings.epic_battle.awards
        with self.viewModel.transaction() as vm:
            vm.setBackground(R.images.gui.maps.icons.epicBattles.backgrounds.reward_selection())
            vm.setTitle(locales.subTitle1() if self.__countBonuses(bonuses) > 1 else locales.subTitle2())
            vm.setSubTitle(locales.title())
            vm.setButtonTitle(locales.acceptButton())
        packBonusModelAndTooltipData(rewards, self.viewModel.mainRewards, self.viewModel.additionalRewards, self.__tooltipItems)

    def _getEvents(self):
        return ((self.viewModel.onAnimationEnded, self.__onAnimationEnded), (self.viewModel.onClose, self.__onClose))

    @args2params(str)
    def __onClose(self, reason):
        if reason == AwardsViewModel.CLOSE_REASON_CANCEL:
            self.__uiEpicBattleLogger.log(EpicBattleLogActions.CLOSE, EpicBattleLogKeys.AWARDS_VIEW, EpicBattleLogKeys.AWARDS_VIEW)
        else:
            self.__uiEpicBattleLogger.log(EpicBattleLogActions.CLICK, EpicBattleLogButtons.AWARDS_OK, EpicBattleLogKeys.AWARDS_VIEW)

    def __onAnimationEnded(self):
        if not self.__isAnimationEnded:
            self.__safeCall(self.__onAnimationEndedCallback)
            self.__isAnimationEnded = True

    @staticmethod
    def __safeCall(callback, *args, **kwargs):
        if callable(callback):
            callback(*args, **kwargs)

    @staticmethod
    def __countBonuses(bonuses):
        return len(bonuses[0].get('items', {})) if bonuses else 0


class AwardsWindow(LobbyNotificationWindow):
    __slots__ = ('__params',)
    __epicController = dependency.descriptor(IEpicBattleMetaGameController)

    def __init__(self, bonuses, onCloseCallback=None, onAnimationEndedCallback=None):
        self.__params = dict(bonuses=bonuses, onCloseCallback=onCloseCallback, onAnimationEndedCallback=onAnimationEndedCallback)
        super(AwardsWindow, self).__init__(wndFlags=WindowFlags.SERVICE_WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=AwardsView(bonuses, onCloseCallback, onAnimationEndedCallback), layer=WindowLayer.TOP_WINDOW)

    def isParamsEqual(self, *args, **kwargs):
        return all((pValue in args or kwargs.get(pName) == pValue for pName, pValue in self.__params.iteritems()))

    def _finalize(self):
        super(AwardsWindow, self)._finalize()
        self.__epicController.onGameModeStatusTick()


def composeBonuses(rewards, ctx=None):
    bonuses = []
    for reward in rewards:
        for key, value in reward.iteritems():
            bonuses.extend(getNonQuestBonuses(key, value, ctx))

    return splitBonuses(mergeBonuses(bonuses))


class FrontlineItemBonusUIPacker(ItemBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, item, count):
        model = super(FrontlineItemBonusUIPacker, cls)._packSingleBonus(bonus, item, count)
        iconName = item.getGUIEmblemID()
        if item.itemTypeID == GUI_ITEM_TYPE.BATTLE_BOOSTER:
            iconName += 'BattleBooster'
        model.setIcon(iconName)
        model.setName(item.getGUIEmblemID())
        model.setType(item.descriptor.itemTypeName)
        return model

    @classmethod
    def _getBonusModel(cls):
        return RewardItemModel()


def getFrontlineBonusPacker():
    mapping = getDefaultBonusPackersMap()
    mapping['items'] = FrontlineItemBonusUIPacker()
    return BonusUIPacker(mapping)


def packBonusModelAndTooltipData(rewards, bonusModelsListMain, bonusModelsListAdditional, tooltipData=None, ctx=None):
    itemsForModel = []
    packer = getFrontlineBonusPacker()
    for bonus in rewards:
        if bonus.isShowInGUI():
            bonusList = packer.pack(bonus)
            bonusTooltipList = []
            bonusContentIdList = []
            if bonusList and tooltipData is not None:
                bonusTooltipList = packer.getToolTip(bonus)
                bonusContentIdList = packer.getContentId(bonus)
            for bonusIndex, item in enumerate(bonusList):
                bonusTooltipData, bonusContentIdData = (None, None)
                if bonusTooltipList:
                    bonusTooltipData = bonusTooltipList[bonusIndex]
                if bonusContentIdList:
                    bonusContentIdData = str(bonusContentIdList[bonusIndex])
                itemsForModel.append((item, bonusTooltipData, bonusContentIdData))

    sortedItems = sorted(itemsForModel, key=lambda item: item[0].getLabel())
    for idx, data in enumerate(sortedItems):
        item, bonusTooltipData, bonusContentIdData = data
        if idx < MAIN_REWARDS_LIMIT:
            item.setIndex(idx)
            bonusModelsListMain.addViewModel(item)
        else:
            item.setIndex(idx - MAIN_REWARDS_LIMIT)
            bonusModelsListAdditional.addViewModel(item)
        tooltipIdx = str(idx)
        item.setTooltipId(tooltipIdx)
        if bonusTooltipList:
            tooltipData[tooltipIdx] = bonusTooltipData
        if bonusContentIdList:
            item.setTooltipContentId(bonusContentIdData)

    return
