# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/dialogs/dialog_template_button.py
import typing
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.backport.backport_tooltip import createBackportTooltipContent
from gui.impl.dialogs.dialog_template_tooltip import DialogTemplateTooltip
from gui.impl.gen import R
from gui.impl.gen.view_models.views.dialogs.dialog_template_button_view_model import ButtonType
from gui.impl.gen.view_models.views.dialogs.dialog_template_button_view_model import DialogTemplateButtonViewModel
from gui.impl.gen.view_models.views.dialogs.custom_sound_button_model import CustomSoundButtonModel
from gui.impl.pub.dialog_window import DialogButtons
from gui.shared.money import Currency
from helpers import dependency
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import Callable, Optional
    from frameworks.wulf import View
    from gui.shared.money import Money

class ButtonPresenter(object):
    __slots__ = ('__tooltip', '_viewModel')

    def __init__(self, label, buttonID, buttonType=ButtonType.PRIMARY, tooltipFactory=None, isBackportTooltip=False, isDisabled=False, *args, **kwargs):
        super(ButtonPresenter, self).__init__()
        self._viewModel = self._getViewModel()
        self._viewModel.setLabel(label)
        self._viewModel.setButtonID(buttonID)
        self._viewModel.setType(buttonType)
        self._viewModel.setIsDisabled(isDisabled)
        self.__tooltip = DialogTemplateTooltip(tooltipFactory, isBackportTooltip)
        self.__tooltip.initialize(self._viewModel.tooltip)

    @property
    def buttonID(self):
        return self._viewModel.getButtonID()

    @property
    def label(self):
        return self._viewModel.getLabel()

    @label.setter
    def label(self, value):
        self.viewModel.setLabel(value)

    @property
    def buttonType(self):
        return self._viewModel.getType()

    @buttonType.setter
    def buttonType(self, value):
        self.viewModel.setType(value)

    @property
    def tooltipFactory(self):
        return self.__tooltip.tooltipFactory

    @tooltipFactory.setter
    def tooltipFactory(self, value):
        self.__tooltip.tooltipFactory = value

    @property
    def isBackportTooltip(self):
        return self.__tooltip.isBackportTooltip

    @isBackportTooltip.setter
    def isBackportTooltip(self, value):
        self.__tooltip.isBackportTooltip = value

    @property
    def isDisabled(self):
        return self._viewModel.getIsDisabled()

    @isDisabled.setter
    def isDisabled(self, value):
        self.viewModel.setIsDisabled(value)

    @property
    def viewModel(self):
        return self._viewModel

    def initialize(self):
        pass

    def dispose(self):
        self._viewModel = None
        self.__tooltip.dispose()
        self.__tooltip = None
        return

    def _getViewModel(self):
        return DialogTemplateButtonViewModel()


class CancelButton(ButtonPresenter):
    __slots__ = ()

    def __init__(self, label=R.strings.dialogs.dialogTemplates.cancel(), buttonID=DialogButtons.CANCEL, buttonType=ButtonType.SECONDARY, tooltipFactory=None, isBackportTooltip=False, isDisabled=False):
        super(CancelButton, self).__init__(label, buttonID, buttonType, tooltipFactory, isBackportTooltip, isDisabled)


class ConfirmButton(ButtonPresenter):
    __slots__ = ()

    def __init__(self, label=R.strings.dialogs.dialogTemplates.confirm(), buttonID=DialogButtons.SUBMIT, buttonType=ButtonType.PRIMARY, tooltipFactory=None, isBackportTooltip=False, isDisabled=False):
        super(ConfirmButton, self).__init__(label, buttonID, buttonType, tooltipFactory, isBackportTooltip, isDisabled)


class CustomSoundButtonPresenter(ButtonPresenter):

    def __init__(self, label, buttonID, buttonType, tooltipFactory, isBackportTooltip, isDisabled, soundClick):
        super(CustomSoundButtonPresenter, self).__init__(label, buttonID, buttonType, tooltipFactory, isBackportTooltip, isDisabled)
        self.viewModel.setSoundClick(soundClick)

    @property
    def viewModel(self):
        return self._viewModel

    def _getViewModel(self):
        return CustomSoundButtonModel()


class CheckMoneyButton(ButtonPresenter):
    __slots__ = ('__money',)
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, money, label=R.strings.dialogs.dialogTemplates.confirm(), buttonID=DialogButtons.SUBMIT, buttonType=ButtonType.PRIMARY, isDisabled=False):
        super(CheckMoneyButton, self).__init__(label, buttonID, buttonType, None, True, isDisabled)
        self.__money = money
        return

    @property
    def money(self):
        return self.__money

    @money.setter
    def money(self, value):
        if self.__money != value:
            self.__money = value
            self._updateButton()

    @property
    def shortage(self):
        return self._itemsCache.items.stats.money.getShortage(self.__money)

    def initialize(self):
        super(CheckMoneyButton, self).initialize()
        g_clientUpdateManager.addMoneyCallback(self._moneyChangeHandler)
        self._updateButton()

    def dispose(self):
        super(CheckMoneyButton, self).dispose()
        g_clientUpdateManager.removeObjectCallbacks(self)

    def _moneyChangeHandler(self, *_):
        self._updateButton()

    def _updateButton(self):
        self.isDisabled = bool(self.shortage.replace(Currency.GOLD, 0))
        if self.isDisabled:
            self.tooltipFactory = self.__notEnoughMoneyTooltipFactory
        else:
            self.tooltipFactory = None
        return

    def __notEnoughMoneyTooltipFactory(self):
        currency = self.shortage.getCurrency()
        return createBackportTooltipContent(TOOLTIPS_CONSTANTS.NOT_ENOUGH_MONEY, (self.shortage.get(currency), currency))


def getConfirmButton(presenter=ButtonPresenter, label=R.strings.dialogs.dialogTemplates.confirm(), buttonID=DialogButtons.SUBMIT, buttonType=ButtonType.PRIMARY, tooltipFactory=None, isBackportTooltip=False, isDisabled=False, *args, **kwargs):
    return presenter(label, buttonID, buttonType, tooltipFactory, isBackportTooltip, isDisabled, *args, **kwargs)
