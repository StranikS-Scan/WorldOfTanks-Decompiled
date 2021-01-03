# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/dialogs/new_year_talisman_gift_dialog.py
from constants import ENDLESS_TOKEN_TIME
from gui import SystemMessages
from gui.battle_pass.battle_pass_award import awardsFactory
from gui.impl.auxiliary.rewards_helper import getBackportTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.views.snow_maidens.snow_maidens_gift_view_model import SnowMaidensGiftViewModel
from gui.impl.gen.view_models.views.lobby.new_year.views.snow_maidens.snow_maidens_gift_view_type import SnowMaidensGiftViewType
from gui.impl.lobby.loot_box.loot_box_bonuses_helpers import packBonusModelAndTooltipData, getLootBoxBonusPacker
from gui.impl.lobby.loot_box.loot_box_sounds import setOverlayHangarGeneral
from gui.impl.lobby.loot_box.loot_box_helper import getTooltipContent
from gui.impl.new_year.new_year_helper import backportTooltipDecorator, TalismanGiftNotifier
from gui.impl.pub.wait_view_impl import WaitViewImpl
from helpers import dependency
from items.components.ny_constants import TOKEN_TALISMAN_BONUS, CurrentNYConstants
from frameworks.wulf import ViewSettings, ViewStatus
from gui.impl.new_year.sounds import NewYearSoundsManager, NewYearSoundEvents
from gui.shared.utils import decorators
from skeletons.new_year import ITalismanSceneController, INewYearController
_ANIMATION_SHOW_CONFIRM_OK = 'show_confirm_ok'

class NewYearTalismanGiftDialogView(WaitViewImpl):
    __slots__ = ('__talismanType', '__dialogType', '__talismanGiftNotifier', '_tooltips')
    __talismanController = dependency.descriptor(ITalismanSceneController)
    __newYearController = dependency.descriptor(INewYearController)

    def __init__(self, talismanType, dialogType=SnowMaidensGiftViewType.SELECT):
        settings = ViewSettings(R.views.lobby.new_year.SnowMaidensGiftView())
        settings.model = SnowMaidensGiftViewModel()
        super(NewYearTalismanGiftDialogView, self).__init__(settings)
        self.__talismanType = talismanType
        self.__dialogType = dialogType
        self._tooltips = {}

    @property
    def viewModel(self):
        return super(NewYearTalismanGiftDialogView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        tooltipData = getBackportTooltipData(event, self._tooltips)
        return getTooltipContent(event, tooltipData)

    @backportTooltipDecorator()
    def createToolTip(self, event):
        return super(NewYearTalismanGiftDialogView, self).createToolTip(event)

    def _onLoading(self):
        super(NewYearTalismanGiftDialogView, self)._onLoading()
        self.__talismanGiftNotifier = TalismanGiftNotifier(self.__updateTalismanGiftCooldown)
        self.__setupDialog()

    def _initialize(self):
        super(NewYearTalismanGiftDialogView, self)._initialize()
        self.__addListeners()
        setOverlayHangarGeneral(True)
        NewYearSoundsManager.setStylesTalismanSwitchBox(self.__talismanType)
        NewYearSoundsManager.playEvent(NewYearSoundEvents.TALISMAN_GIFT)

    def _finalize(self):
        NewYearSoundsManager.playEvent(NewYearSoundEvents.TALISMAN_GIFT_EXIT)
        setOverlayHangarGeneral(False)
        self.__talismanGiftNotifier.stopNotification()
        self.__talismanGiftNotifier.clear()
        self.__removeListeners()
        super(NewYearTalismanGiftDialogView, self)._finalize()

    def _getDefaultResult(self):
        return (False, self.__dialogType == SnowMaidensGiftViewType.CONGRAT)

    def __addListeners(self):
        self.viewModel.onBackToTree += self.__onBackToTree
        self.viewModel.onClose += self.__onClose
        self.viewModel.onTakeGift += self.__onTakeGift

    def __removeListeners(self):
        self.viewModel.onBackToTree -= self.__onBackToTree
        self.viewModel.onClose -= self.__onClose
        self.viewModel.onTakeGift -= self.__onTakeGift

    def __getResult(self, toTree):
        return (toTree, self.__dialogType == SnowMaidensGiftViewType.CONGRAT)

    def __onBackToTree(self, _=None):
        self._setResult(result=self.__getResult(toTree=True))

    def __onClose(self, _=None):
        self._setResult(result=self.__getResult(toTree=False))

    def __onTakeGift(self, _=None):
        self.__takeGift()

    def __setupDialog(self, rewards=None):
        with self.viewModel.transaction() as model:
            model.setSnowMaidenType(self.__talismanType)
            model.setDialogType(self.__dialogType)
            model.setProgressLevel(self.__newYearController.getTalismanProgressLevel())
            model.setSnowMaidensAmount(len(self.__newYearController.getTalismans(isInInventory=True)))
            if self.__dialogType == SnowMaidensGiftViewType.CONGRAT:
                self.__talismanGiftNotifier.startNotification()
                rewardsList = model.getRewards()
                rewardsList.clear()
                packBonusModelAndTooltipData(rewards, rewardsList, getLootBoxBonusPacker(isExtra=True), self._tooltips)
                rewardsList.invalidate()
                model.setIsLastDay(self.__newYearController.isLastDayOfEvent())

    @staticmethod
    def __convertGiftToBonuses(rawData):
        toyID, tokenCount = rawData
        token = {'expires': {'at': ENDLESS_TOKEN_TIME},
         'count': tokenCount}
        rewards = {CurrentNYConstants.TOYS: {toyID: 1},
         'tokens': {TOKEN_TALISMAN_BONUS: token}}
        return awardsFactory(rewards)

    @decorators.process('updating')
    def __takeGift(self):
        from new_year.ny_processor import GetTalismanToyProcessor
        result = yield GetTalismanToyProcessor(self.__talismanType).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
        if result.success:
            self.__talismanController.setGiftAnimationState(self.__talismanType, _ANIMATION_SHOW_CONFIRM_OK)
        if self.viewStatus != ViewStatus.LOADED:
            return
        if result.success:
            converted = self.__convertGiftToBonuses(result.auxData)
            self.__initCongratsFlow(converted)
        else:
            self.destroyWindow()

    def __initCongratsFlow(self, rewards):
        self.__dialogType = SnowMaidensGiftViewType.CONGRAT
        self.__setupDialog(rewards)
        NewYearSoundsManager.playEvent(NewYearSoundEvents.TALISMAN_RECEIVING_GIFT)

    def __updateTalismanGiftCooldown(self, cooldown):
        self.viewModel.setCooldown(cooldown)
