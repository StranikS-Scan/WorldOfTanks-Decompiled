# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/battle_pass_reward_choice_view.py
from adisp import process
from battle_pass_common import BATTLE_PASS_TOKEN_BLUEPRINT_OFFER, BATTLE_PASS_TOKEN_BROCHURE_OFFER, BATTLE_PASS_TOKEN_GUIDE_OFFER, BATTLE_PASS_TOKEN_NEW_DEVICE_OFFER, BATTLE_PASS_TOKEN_TROPHY_OFFER
from frameworks.wulf import ViewSettings, WindowFlags
from gui import SystemMessages
from gui.battle_pass.battle_pass_decorators import createBackportTooltipDecorator
from gui.battle_pass.battle_pass_helpers import getOfferTokenByGift
from gui.battle_pass.battle_pass_reward_option_packers import BattlePassRewardOptionType, packRewardOptionModel
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.battle_pass_reward_choice_view_model import BattlePassRewardChoiceViewModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared.event_dispatcher import showBattlePassRewardChoiceWindow
from gui.shared.gui_items.processors.offers import ReceiveOfferGiftProcessor
from gui.sounds.filters import switchHangarOverlaySoundFilter
from helpers import dependency
from skeletons.gui.game_control import IBattlePassController
from skeletons.gui.offers import IOffersDataProvider
_OFFER_MAIN_TOKEN_TO_REWARD_TYPE = {BATTLE_PASS_TOKEN_BLUEPRINT_OFFER: BattlePassRewardOptionType.BLUEPRINT,
 BATTLE_PASS_TOKEN_BROCHURE_OFFER: BattlePassRewardOptionType.CREW_BROCHURE,
 BATTLE_PASS_TOKEN_GUIDE_OFFER: BattlePassRewardOptionType.CREW_GUIDE,
 BATTLE_PASS_TOKEN_NEW_DEVICE_OFFER: BattlePassRewardOptionType.NEW_DEVICE,
 BATTLE_PASS_TOKEN_TROPHY_OFFER: BattlePassRewardOptionType.TROPHY_DEVICE}

class BattlePassRewardChoiceView(ViewImpl):
    __slots__ = ('__offer', '__tooltips', '__rewardType')
    __battlePassController = dependency.descriptor(IBattlePassController)
    __offersProvider = dependency.descriptor(IOffersDataProvider)

    def __init__(self, layoutID, *args, **kwargs):
        settings = ViewSettings(layoutID)
        settings.model = BattlePassRewardChoiceViewModel()
        settings.args = args
        settings.kwargs = kwargs
        self.__offer = None
        self.__tooltips = {}
        super(BattlePassRewardChoiceView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(BattlePassRewardChoiceView, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(BattlePassRewardChoiceView, self).createToolTip(event)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltips.get(tooltipId)

    def _onLoading(self, *args, **kwargs):
        super(BattlePassRewardChoiceView, self)._onLoading(*args, **kwargs)
        self.__addListeners()
        self.__setMainData()

    def _finalize(self):
        switchHangarOverlaySoundFilter(on=False)
        self.__removeListeners()
        super(BattlePassRewardChoiceView, self)._finalize()

    def __setMainData(self):
        offerToken = getOfferTokenByGift(self.__battlePassController.getRewardLogic().getNextRewardToChoose())
        self.__offer = self.__offersProvider.getOfferByToken(offerToken)
        offerTokenPrefix, _, level = self.__offer.token.rsplit(':', 2)
        level = int(level)
        self.__rewardType = _OFFER_MAIN_TOKEN_TO_REWARD_TYPE[offerTokenPrefix + ':']
        with self.viewModel.transaction() as model:
            model.setRewardType(backport.text(R.strings.battle_pass_2020.rewardChoice.rewardType.dyn(self.__rewardType.value)()))
            model.setLevel(level)
            chapter = self.__battlePassController.getChapterByLevel(level)
            model.setChapter(backport.text(R.strings.battle_pass_2020.chapter.name.num(chapter)()))
            model.setChapterNumber(chapter)
            model.setIsOptionsSequence(self.__battlePassController.getRewardLogic().hasRewardToChoose())
            model.setSelectedGiftId(-1)
            self.__fillRewards(model=model)
        switchHangarOverlaySoundFilter(on=True)

    def __addListeners(self):
        self.viewModel.onTakeClick += self.__onTakeClick
        self.viewModel.onCloseClick += self.__onCloseClick
        self.viewModel.onAnimationFinished += self.__onAnimationFinished

    def __removeListeners(self):
        self.viewModel.onTakeClick -= self.__onTakeClick
        self.viewModel.onCloseClick -= self.__onCloseClick
        self.viewModel.onAnimationFinished -= self.__onAnimationFinished

    @replaceNoneKwargsModel
    def __fillRewards(self, model=None):
        self.__tooltips.clear()
        model.rewards.clearItems()
        gifts = {gift.id:gift.bonuses[0] for gift in self.__offer.getAllGifts()}
        packRewardOptionModel(self.__rewardType, gifts, model.rewards, self.__tooltips)

    def __onCloseClick(self):
        self.__processNext(False)

    @process
    def __onTakeClick(self, args):
        giftId = args.get('giftId')
        if giftId is None:
            return
        else:
            giftId = int(giftId)
            result = yield ReceiveOfferGiftProcessor(self.__offer.id, giftId, skipConfirm=True).request()
            if result.success:
                if result.auxData:
                    self.__battlePassController.getRewardLogic().addRewards(result.auxData)
                self.viewModel.setSelectedGiftId(giftId)
            else:
                SystemMessages.pushI18nMessage(backport.text(R.strings.system_messages.battlePass.rewardChoice.error()), type=SystemMessages.SM_TYPE.Error)
            return

    def __onAnimationFinished(self):
        self.__processNext(True)

    def __processNext(self, isRewardTaken):
        self.__battlePassController.getRewardLogic().removeRewardToChoose(self.__offer.giftToken, isRewardTaken)
        if self.__battlePassController.getRewardLogic().hasRewardToChoose():
            showBattlePassRewardChoiceWindow()
        else:
            self.__battlePassController.getRewardLogic().postStateEvent()
        self.destroyWindow()


class BattlePassRewardChoiceWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self):
        super(BattlePassRewardChoiceWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=BattlePassRewardChoiceView(layoutID=R.views.lobby.battle_pass.BattlePassRewardChoiceView()))
