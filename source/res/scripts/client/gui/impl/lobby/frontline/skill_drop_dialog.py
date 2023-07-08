# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/frontline/skill_drop_dialog.py
from gui.impl import backport
from gui.impl.dialogs.dialog_template import DialogTemplateView
from gui.impl.dialogs.dialog_template_button import CancelButton, CheckMoneyButton, ConfirmButton
from gui.impl.dialogs.sub_views.content.simple_text_content import SimpleTextContent
from gui.impl.dialogs.sub_views.footer.simple_text_footer import SimpleTextFooter
from gui.impl.dialogs.sub_views.footer.single_price_footer import SinglePriceFooter
from gui.impl.dialogs.sub_views.title.simple_text_title import SimpleTextTitle
from gui.impl.dialogs.sub_views.top_right.money_balance import MoneyBalance
from gui.impl.gen import R
from gui.impl.gen.view_models.views.dialogs.default_dialog_place_holders import DefaultDialogPlaceHolders as Placeholder
from gui.impl.gen.view_models.views.dialogs.dialog_template_button_view_model import ButtonType
from gui.impl.gen.view_models.views.dialogs.sub_views.currency_view_model import CurrencySize
from gui.impl.lobby.frontline.dialogs.blank_price_view import BlankPriceView
from gui.impl.pub.dialog_window import DialogButtons
from gui.shared.gui_items.gui_item_economics import ItemPrice
from gui.shared.money import Money, Currency
from gui.shop import showBuyGoldForCrew
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from uilogging.epic_battle.constants import EpicBattleLogKeys, EpicBattleLogActions
from uilogging.epic_battle.loggers import EpicBattleTooltipLogger
BLANK_COST_COUNT = 1
FULL_REUSE = 100

class SkillDropDialog(DialogTemplateView):
    __appLoader = dependency.descriptor(IAppLoader)
    __slots__ = ('__tankman', '__isBlank', '__price', '__freeDropSave100', '__uiEpicBattleLogger')
    _itemsCache = dependency.descriptor(IItemsCache)
    _lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, tankman, price=None, isBlank=False, freeDropSave100=False, layoutID=None, uniqueID=None):
        super(SkillDropDialog, self).__init__(layoutID, uniqueID)
        self.__isBlank = isBlank
        self.__price = price
        self.__tankman = tankman
        self.__freeDropSave100 = freeDropSave100
        self.__uiEpicBattleLogger = EpicBattleTooltipLogger()

    @property
    def itemPrice(self):
        return ItemPrice(Money(**self.__price), Money(**self.__price))

    def _onLoading(self, *args, **kwargs):
        money = Money(**self.__price) if self.__price else None
        self.setSubView(Placeholder.TITLE, SimpleTextTitle(R.strings.dialogs.dropSkill.fullscreen.title()))
        if not self.__freeDropSave100:
            skillPercent = FULL_REUSE if self.__isBlank else int(self.__price.get('xpReuseFraction', 1) * FULL_REUSE)
            self.setSubView(Placeholder.CONTENT, SimpleTextContent(backport.text(R.strings.dialogs.dropSkill.fullscreen.description(), skillPercent=skillPercent)))
        if not self.__isBlank or self.__freeDropSave100:
            if money and not self.__freeDropSave100:
                self.setSubView(Placeholder.TOP_RIGHT, MoneyBalance())
                self.setSubView(Placeholder.FOOTER, SinglePriceFooter(R.strings.dialogs.common.cost, self.itemPrice, CurrencySize.BIG))
                self.addButton(CheckMoneyButton(money, R.strings.dialogs.dropSkill.fullscreen.ok(), buttonType=ButtonType.MAIN if money.gold > 0 else ButtonType.PRIMARY))
            else:
                self.setSubView(Placeholder.FOOTER, SimpleTextFooter(R.strings.dialogs.dropSkill.fullscreen.costFree()))
                self.addButton(ConfirmButton(R.strings.dialogs.dropSkill.fullscreen.ok()))
        else:
            self.setSubView(Placeholder.FOOTER, BlankPriceView(BLANK_COST_COUNT))
            self.addButton(ConfirmButton(R.strings.dialogs.dropSkill.fullscreen.ok()))
        self.addButton(CancelButton())
        super(SkillDropDialog, self)._onLoading(*args, **kwargs)
        self.__uiEpicBattleLogger.log(EpicBattleLogActions.OPEN.value, item=EpicBattleLogKeys.DROP_SKILL_DIALOG_CONFIRM.value, parentScreen=EpicBattleLogKeys.HANGAR.value)
        self.__uiEpicBattleLogger.initialize(EpicBattleLogKeys.DROP_SKILL_DIALOG_CONFIRM.value)
        return

    def _initialize(self):
        super(SkillDropDialog, self)._initialize()
        self._lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange

    def _finalize(self):
        self._lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange
        super(SkillDropDialog, self)._finalize()
        self.__uiEpicBattleLogger.reset()

    def _setResult(self, result):
        self.__uiEpicBattleLogger.log(EpicBattleLogActions.CLICK.value, item=result, parentScreen=EpicBattleLogKeys.DROP_SKILL_DIALOG_CONFIRM.value, info='blanks' if self.__isBlank else ('free' if self.__freeDropSave100 else self.itemPrice.price.getCurrency()))
        if result == DialogButtons.SUBMIT and not self.__isBlank and not self.__freeDropSave100:
            shortage = self._itemsCache.items.stats.money.getShortage(self.itemPrice.price)
            if shortage and shortage.getCurrency() == Currency.GOLD:
                showBuyGoldForCrew(self.itemPrice.price.gold)
                result = DialogButtons.CANCEL
        super(SkillDropDialog, self)._setResult(result)

    def __onServerSettingsChange(self, diff):
        if 'recertificationFormState' in diff:
            self.destroyWindow()
