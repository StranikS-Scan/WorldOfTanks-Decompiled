# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/tooltips/ny_attachments_statistics_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_reward_kit_statistics_reward_model import Type
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_attachments_statistics_tooltip_model import NyAttachmentsStatisticsTooltipModel
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_loot_box_statistics_attachment_model import NyLootBoxStatisticsAttachmentModel
from gui.impl.lobby.loot_box.loot_box_helper import getLootboxStatisticsKey
from gui.impl.pub import ViewImpl
from gui.shared.gui_items import GUI_ITEM_TYPE, GUI_ITEM_TYPE_NAMES
from helpers import dependency
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.shared import IItemsCache

class NyAttachmentsStatisticsTooltip(ViewImpl):
    __slots__ = ('__lootboxID',)
    __itemsCache = dependency.descriptor(IItemsCache)
    __c11n = dependency.descriptor(ICustomizationService)

    def __init__(self, lootboxID, layoutID=R.views.lobby.new_year.tooltips.NyAttachmentsStatisticsTooltip()):
        settings = ViewSettings(layoutID)
        settings.model = NyAttachmentsStatisticsTooltipModel()
        super(NyAttachmentsStatisticsTooltip, self).__init__(settings)
        self.__lootboxID = lootboxID

    @property
    def viewModel(self):
        return super(NyAttachmentsStatisticsTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        with self.viewModel.transaction() as model:
            modelAttachments = model.getAttachments()
            statsKey = getLootboxStatisticsKey(self.__lootboxID)
            if statsKey is not None:
                lootboxStats = self.__itemsCache.items.tokens.getLootBoxesStats().get(statsKey)
                if lootboxStats is not None:
                    lootboxRewards, _, __ = lootboxStats
                    for customizationsData in lootboxRewards.get(Type.CUSTOMIZATIONS.value, {}):
                        if 'compensatedNumber' in customizationsData or customizationsData['custType'] != GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.ATTACHMENT]:
                            continue
                        attachment = self.__c11n.getItemByID(GUI_ITEM_TYPE.ATTACHMENT, customizationsData['id'])
                        attachmentModel = NyLootBoxStatisticsAttachmentModel()
                        attachmentModel.setName(attachment.userName)
                        attachmentModel.setAmount(customizationsData.get('value', 0))
                        attachmentModel.setRarity(attachment.rarity)
                        modelAttachments.addViewModel(attachmentModel)

            modelAttachments.invalidate()
        return
