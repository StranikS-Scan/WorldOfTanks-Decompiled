# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/dialogs/challenge/guest_quest_purchase_confirm.py
from frameworks.wulf import ViewSettings
from gui.game_control.wallet import WalletController
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_resource_model import NyResourceModel
from gui.impl.gen.view_models.views.lobby.new_year.dialogs.challenge.buy_celebrity_quest_item_dialog_model import BuyCelebrityQuestItemDialogModel, ResourceType, DialogState
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogBaseView
from gui.impl.lobby.new_year.tooltips.ny_market_lack_the_res_tooltip import NyMarketLackTheResTooltip
from gui.impl.lobby.new_year.tooltips.ny_resource_tooltip import NyResourceTooltip
from gui.impl.new_year.new_year_helper import backportTooltipDecorator
from gui.impl.pub.dialog_window import DialogButtons
from helpers import dependency
from items.components.ny_constants import NyCurrency
from new_year.celebrity.celebrity_quests_helpers import GuestsQuestsConfigHelper
from skeletons.gui.game_control import IWalletController
from skeletons.new_year import INewYearController

class GuestQuestPurchaseDialogView(FullScreenDialogBaseView):
    _nyController = dependency.descriptor(INewYearController)
    _wallet = dependency.descriptor(IWalletController)

    def __init__(self, guestName, questIndex, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.dialogs.challenge.BuyCelebrityQuestItemDialog())
        settings.args = args
        settings.kwargs = kwargs
        settings.model = BuyCelebrityQuestItemDialogModel()
        self.__guestName = guestName
        self.__questIndex = questIndex
        super(GuestQuestPurchaseDialogView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(GuestQuestPurchaseDialogView, self).getViewModel()

    @backportTooltipDecorator()
    def createToolTip(self, event):
        return super(GuestQuestPurchaseDialogView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        tooltips = R.views.lobby.new_year.tooltips
        if contentID == tooltips.NyMarketLackTheResTooltip():
            return NyMarketLackTheResTooltip(str(event.getArgument('resourceType')), int(event.getArgument('price')))
        if contentID == tooltips.NyResourceTooltip():
            resourceType = event.getArgument('type')
            return NyResourceTooltip(resourceType)
        return super(GuestQuestPurchaseDialogView, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        super(GuestQuestPurchaseDialogView, self)._onLoading(*args, **kwargs)
        self.__fillModel()

    def _getEvents(self):
        return ((self.viewModel.onAccept, self._onAccept),
         (self.viewModel.onCancel, self._onCancel),
         (self._nyController.currencies.onBalanceUpdated, self.__onBalanceUpdated),
         (self._wallet.onWalletStatusChanged, self.__onWalletStatusChanged))

    def __fillModel(self):
        questsHolder = GuestsQuestsConfigHelper.getNYQuestsByGuest(self.__guestName)
        quest = questsHolder.getQuestByQuestIndex(self.__questIndex)
        currency, price = GuestsQuestsConfigHelper.getQuestPrice(quest)
        with self.viewModel.transaction() as model:
            resources = model.getResources()
            resources.clear()
            for currency_ in NyCurrency.ALL:
                resource = NyResourceModel()
                resource.setType(currency_)
                resource.setValue(self._nyController.currencies.getResouceBalance(currency_))
                resources.addViewModel(resource)

            resources.invalidate()
            model.setQuestId(quest.getQuestID())
            model.setPrice(price)
            model.setResourceType(self.__getResourceType(currency))
            self.__updateState(model)

    def __onBalanceUpdated(self):
        self.__fillModel()

    def __onWalletStatusChanged(self, *_):
        with self.viewModel.transaction() as model:
            self.__updateState(model)

    def __getResourceType(self, resourceValue):
        for recource in ResourceType:
            if resourceValue == recource.value:
                return recource

    def __updateState(self, model):
        questsHolder = GuestsQuestsConfigHelper.getNYQuestsByGuest(self.__guestName)
        quest = questsHolder.getQuestByQuestIndex(self.__questIndex)
        currency, price = GuestsQuestsConfigHelper.getQuestPrice(quest)
        currencyStatus = self._wallet.dynamicComponentsStatuses.get(currency)
        if self._wallet.isNotAvailable:
            status = DialogState.NOWALLET
        elif currencyStatus != WalletController.STATUS.AVAILABLE:
            status = DialogState.NOWALLET
        elif price > self._nyController.currencies.getResouceBalance(currency):
            status = DialogState.NOTENOUGHMONEY
        else:
            status = DialogState.DEFAULT
        model.setDialogState(status)

    def _onAccept(self):
        self._setResult(DialogButtons.SUBMIT)

    def _onCancel(self):
        self._setResult(DialogButtons.CANCEL)
