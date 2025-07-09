# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/impl/lobby/birthday/all_rewards_view.py
from helpers import dependency
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from frameworks.wulf import ViewFlags, ViewSettings
from mt_birthday.gui.impl.gen.view_models.views.lobby.birthday.all_rewards_view_model import AllRewardsViewModel
from mt_birthday.gui.impl.gen.view_models.views.lobby.tooltips.advanced_simple_tooltip_model import AdvancedSimpleTooltipModel
from mt_birthday.gui.impl.gen.view_models.views.lobby.tooltips.gold_ticket_tooltip_model import GoldTicketTooltipModel
from mt_birthday.skeletons.mt_birthday_controller import ITanksBirthdayController
from mt_birthday.gui.birthday_helpers.birthday_model_helpers import fillChapterLevelsModel
from skeletons.gui.shared import IItemsCache

class AllRewardsView(ViewImpl):
    __mtBirthday = dependency.descriptor(ITanksBirthdayController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ('__tooltipData',)

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = AllRewardsViewModel()
        super(AllRewardsView, self).__init__(settings)
        self.__tooltipData = {}

    @property
    def viewModel(self):
        return super(AllRewardsView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        self.__updateModel()
        super(AllRewardsView, self)._onLoading(*args, **kwargs)

    def _getEvents(self):
        return ((self.__mtBirthday.progression.onProgressionUpdated, self.__onProgressionUpdated),)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.mt_birthday.lobby.tooltips.GoldTicketTooltip():
            goldTicketTooltipModel = GoldTicketTooltipModel()
            settings = ViewSettings(layoutID=R.views.mt_birthday.lobby.tooltips.GoldTicketTooltip(), model=goldTicketTooltipModel)
            return ViewImpl(settings)
        elif contentID == R.views.mt_birthday.lobby.tooltips.AdvancedSimpleTooltip():
            advancedSimpleTooltipModel = AdvancedSimpleTooltipModel()
            advancedSimpleTooltipModel.setHeader(event.getArgument('header', ''))
            advancedSimpleTooltipModel.setDescription(event.getArgument('description', ''))
            advancedSimpleTooltipModel.setAdditionalDescription(event.getArgument('additionalDescription', ''))
            settings = ViewSettings(layoutID=R.views.mt_birthday.lobby.tooltips.AdvancedSimpleTooltip(), model=advancedSimpleTooltipModel)
            return ViewImpl(settings)
        elif contentID == R.views.gui_lootboxes.lobby.gui_lootboxes.tooltips.LootboxTooltip():
            from gui_lootboxes.gui.impl.lobby.gui_lootboxes.tooltips.lootbox_tooltip import LootboxTooltip
            tooltipData = self.getTooltipData(event)
            lootBoxID = tooltipData.get('lootBoxID')
            lootBox = self.__itemsCache.items.tokens.getLootBoxByID(int(lootBoxID))
            return LootboxTooltip(lootBox)
        else:
            return None

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltipData.get(tooltipId)

    def __onProgressionUpdated(self):
        self.__updateModel()

    def __updateModel(self):
        with self.viewModel.transaction() as tx:
            fillChapterLevelsModel(tx, tooltipData=self.__tooltipData)
