# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/customization/attachments_preview/attachments_preview.py
from __future__ import absolute_import
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.backport import createTooltipData
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.customization.attachments_preview.attachment_bonus_model import AttachmentBonusModel
from gui.impl.gen.view_models.views.lobby.customization.attachments_preview.attachments_preview_model import AttachmentsPreviewModel
from gui.impl.pub import ViewImpl, WindowImpl
from gui.server_events.bonuses import parseAttachmentsSetToken
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.customization import CustomizationTooltipContext
from gui.shared.missions.packers.bonus import BACKPORT_TOOLTIP_CONTENT_ID
from helpers import dependency
from items.components.c11n_constants import Rarity
from skeletons.gui.customization import ICustomizationService
_RARITY_PRIORITY = {rarity:idx for idx, rarity in enumerate(Rarity.FILTERABLE)}

class AttachmentsPreview(ViewImpl):
    __customization = dependency.descriptor(ICustomizationService)
    LAYOUT_ID = R.views.mono.attachments_preview.attachments_preview()

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(self.LAYOUT_ID, model=AttachmentsPreviewModel(), args=args, kwargs=kwargs)
        super(AttachmentsPreview, self).__init__(settings)
        self.__tooltips = {}

    @property
    def viewModel(self):
        return super(AttachmentsPreview, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(AttachmentsPreview, self).createToolTip(event)

    def getTooltipData(self, event):
        return self.__tooltips.get(event.getArgument('tooltipId', ''))

    def _onLoading(self, setTokenID, *args, **kwargs):
        super(AttachmentsPreview, self)._onLoading(*args, **kwargs)
        self.__fillModel(setTokenID)

    def _finalize(self):
        super(AttachmentsPreview, self)._finalize()
        self.__tooltips.clear()

    def __fillModel(self, setTokenID):
        with self.viewModel.transaction() as model:
            setName, attachmentIDs = parseAttachmentsSetToken(setTokenID)
            model.setAttachmentSetID(setName)
            attachmentsModel = model.getAttachments()
            attachmentsModel.clear()
            self.__tooltips.clear()
            for attachment in self.__getSortedAttachments(attachmentIDs):
                attachmentsModel.addViewModel(self.__packAttachment(attachment))

    def __getSortedAttachments(self, attachmentIDs):
        attachments = [ self.__customization.getItemByID(GUI_ITEM_TYPE.ATTACHMENT, attachmentID) for attachmentID in attachmentIDs ]
        attachments.sort(key=lambda attachment: _RARITY_PRIORITY.get(attachment.rarity, len(_RARITY_PRIORITY)))
        return attachments

    def __packAttachment(self, attachment):
        bonusModel = AttachmentBonusModel()
        bonusModel.setId(attachment.id)
        bonusModel.setTooltipId(str(attachment.id))
        bonusModel.setTooltipContentId(str(BACKPORT_TOOLTIP_CONTENT_ID))
        bonusModel.setName(attachment.itemTypeName)
        bonusModel.setIcon(attachment.name)
        bonusModel.setOverlayType(attachment.rarity)
        bonusModel.setLabel(attachment.userName)
        specialAlias = TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_AWARD
        specialArgs = CustomizationTooltipContext(itemCD=attachment.intCD)
        self.__tooltips[str(attachment.id)] = createTooltipData(None, True, specialAlias, specialArgs)
        return bonusModel


class AttachmentsPreviewWindow(WindowImpl):

    def __init__(self, setTokenID):
        super(AttachmentsPreviewWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, layer=WindowLayer.FULLSCREEN_WINDOW, content=AttachmentsPreview(setTokenID))
