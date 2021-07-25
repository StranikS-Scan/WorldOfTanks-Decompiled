# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/dialogs/recover_instructor_dialog_view.py
import typing
import nations
from frameworks.wulf import ViewSettings
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.auxiliary.instructors_helper import getInstructorPageBackground
from gui.impl.backport.backport_tooltip import createBackportTooltipContent
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.dialogs.recover_instructor_dialog_view_model import RecoverInstructorDialogViewModel
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogView
from gui.shared.gui_items.detachment import Detachment
from gui.shared.gui_items.instructor import Instructor
from gui.shared.money import Currency
from gui.shop import showBuyGoldForDetachmentRecoverInstructor
from helpers.dependency import descriptor
from skeletons.gui.detachment import IDetachmentCache
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.detachment.common.price_model import PriceModel

class RecoverInstructorDialogView(FullScreenDialogView):
    __itemsCache = descriptor(IItemsCache)
    __detachmentCache = descriptor(IDetachmentCache)
    __slots__ = ('_detachment', '_instructorInvID', '_isInBarracks')

    def __init__(self, ctx):
        settings = ViewSettings(R.views.lobby.detachment.dialogs.RecoverInstructorDialogView())
        settings.model = RecoverInstructorDialogViewModel()
        super(RecoverInstructorDialogView, self).__init__(settings)
        self._detachment = None
        self._instructorInvID = ctx.get('instructorInvID')
        self._isInBarracks = ctx.get('isInBarracks', False)
        return

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            if tooltipId == TOOLTIPS_CONSTANTS.NOT_ENOUGH_MONEY:
                currency = event.getArgument('currency')
                value = int(event.getArgument('value', 0))
                shortage = max(value - self.__itemsCache.items.stats.money.get(currency, 0), 0)
                return createBackportTooltipContent(TOOLTIPS_CONSTANTS.NOT_ENOUGH_MONEY, (shortage, currency))
        return super(RecoverInstructorDialogView, self).createToolTipContent(event, contentID)

    def _addListeners(self):
        super(RecoverInstructorDialogView, self)._addListeners()
        g_clientUpdateManager.addMoneyCallback(self.__updateIsEnoughStatus)

    def _removeListeners(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(RecoverInstructorDialogView, self)._removeListeners()

    @property
    def viewModel(self):
        return super(RecoverInstructorDialogView, self).getViewModel()

    def _getInstructor(self):
        return self.__detachmentCache.getInstructor(self._instructorInvID)

    def _getInstructorSlotID(self):
        instructor = self._getInstructor()
        detachment = self.__detachmentCache.getDetachment(instructor.detInvID)
        instructorsIDs = detachment.getInstructorsIDs()
        return instructorsIDs.index(self._instructorInvID)

    def _setBaseParams(self, model):
        with model.transaction() as viewModel:
            instructor = self._getInstructor()
            model.setBackground(getInstructorPageBackground(instructor.pageBackground))
            model.setIcon(instructor.getPortraitName())
            model.setNation(nations.MAP[instructor.nationID])
            self._updatePrice(viewModel.priceModel)
            viewModel.setAcceptButtonText(R.strings.detachment.instructorPage.recover())
            viewModel.setCancelButtonText(R.strings.dialogs.detachment.demountInstructor.cancel())
            viewModel.setIsInBarracks(self._isInBarracks)
            super(RecoverInstructorDialogView, self)._setBaseParams(model)

    def __updateIsEnoughStatus(self, *_):
        with self.viewModel.transaction() as viewModel:
            self._updatePrice(viewModel.priceModel)

    def _updatePrice(self, priceModel):
        recoverInstructorCost = self.__itemsCache.items.shop.recoverInstructorCost
        playerMoney = self.__itemsCache.items.stats.money
        hasEnoughMoney = True
        for currency in Currency.GUI_ALL:
            if recoverInstructorCost.isSet(currency):
                currencyCost = recoverInstructorCost.get(currency)
                priceModel.setValue(currencyCost)
                priceModel.setType(currency)
                if currencyCost > playerMoney.get(currency, default=0):
                    hasEnoughMoney = False
                break

        priceModel.setIsEnough(hasEnoughMoney)

    def _onAcceptClicked(self):
        recoverMoney = self.__itemsCache.items.shop.recoverInstructorCost
        currency = recoverMoney.getCurrency(byWeight=True)
        recPrice = recoverMoney.get(currency)
        playerCurrency = self.__itemsCache.items.stats.money.get(currency)
        if playerCurrency < recPrice:
            if currency == Currency.GOLD:
                showBuyGoldForDetachmentRecoverInstructor(recPrice)
            return
        super(RecoverInstructorDialogView, self)._onAcceptClicked()
