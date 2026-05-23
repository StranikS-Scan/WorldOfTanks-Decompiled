# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: open_bundle/scripts/client/open_bundle/gui/impl/lobby/attachments_preview.py
from __future__ import absolute_import
from frameworks.wulf import ViewSettings, WindowLayer, WindowFlags
from open_bundle.gui.impl.gen.view_models.views.lobby.attachments_preview_model import AttachmentsPreviewModel
from open_bundle.gui.impl.gen.view_models.views.lobby.bonus_model import BonusModel
from open_bundle.helpers.bonuses.bonus_packers import parseAttachmentToken
from open_bundle.skeletons.open_bundle_controller import IOpenBundleController
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.backport import createTooltipData
from gui.impl.gen import R
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.pub import ViewImpl, WindowImpl
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.customization import CustomizationTooltipContext
from gui.shared.missions.packers.bonus import BACKPORT_TOOLTIP_CONTENT_ID
from helpers import dependency
from items.components.c11n_constants import Rarity
from skeletons.gui.customization import ICustomizationService
RARITY_PRIORITY = {rarity:idx for idx, rarity in enumerate(Rarity.FILTERABLE)}

class AttachmentsPreview(ViewImpl):
    __customization = dependency.descriptor(ICustomizationService)
    __openBundle = dependency.descriptor(IOpenBundleController)

    def __init__(self, bundleID, attachmentsToken):
        settings = ViewSettings(R.views.open_bundle.mono.lobby.attachments_preview(), model=AttachmentsPreviewModel())
        self.__bundleID = bundleID
        self.__attachmentsToken = attachmentsToken
        self.__tooltips = {}
        super(AttachmentsPreview, self).__init__(settings)

    @property
    def viewModel(self):
        return super(AttachmentsPreview, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(AttachmentsPreview, self).createToolTip(event)

    def getTooltipData(self, event):
        return self.__tooltips.get(event.getArgument('tooltipId', 0))

    def _onLoading(self, *args, **kwargs):
        super(AttachmentsPreview, self)._onLoading(*args, **kwargs)
        self.__fillModel()

    def __fillModel(self):
        with self.viewModel.transaction() as model:
            model.setBundleType(self.__openBundle.config.getBundle(self.__bundleID).type)
            name, attachmentsIDs = parseAttachmentToken(self.__attachmentsToken)
            model.setName(name)
            sortedIDs = sorted(attachmentsIDs, key=lambda attachmentID: RARITY_PRIORITY.get(self.__customization.getItemByID(GUI_ITEM_TYPE.ATTACHMENT, int(attachmentID)).rarity, len(RARITY_PRIORITY)))
            for attachmentID in sortedIDs:
                attachmentModel = BonusModel()
                self.__packAttachment(attachmentModel, attachmentID)
                model.getAttachments().addViewModel(attachmentModel)

    def __packAttachment(self, bonusModel, attachmentID):
        attachment = self.__customization.getItemByID(GUI_ITEM_TYPE.ATTACHMENT, int(attachmentID))
        bonusModel.setId(int(attachmentID))
        bonusModel.setTooltipId(str(attachmentID))
        bonusModel.setTooltipContentId(str(BACKPORT_TOOLTIP_CONTENT_ID))
        bonusModel.setName(attachment.itemTypeName)
        bonusModel.setIcon(attachment.name)
        bonusModel.setOverlayType(attachment.rarity)
        bonusModel.setLabel(attachment.userName)
        specialAlias = TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_AWARD
        specialArgs = CustomizationTooltipContext(itemCD=attachment.intCD)
        self.__tooltips[str(attachmentID)] = createTooltipData(None, True, specialAlias, specialArgs)
        return


class AttachmentsPreviewWindow(WindowImpl):

    def __init__(self, bundleID, attachmentsToken):
        super(AttachmentsPreviewWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, layer=WindowLayer.FULLSCREEN_WINDOW, content=AttachmentsPreview(bundleID=bundleID, attachmentsToken=attachmentsToken))
