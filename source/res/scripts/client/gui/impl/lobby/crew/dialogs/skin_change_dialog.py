# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/dialogs/skin_change_dialog.py
from base_crew_dialog_template_view import BaseCrewDialogTemplateView
from gui.impl import backport
from gui.impl.dialogs.dialog_template_button import CancelButton, ConfirmButton
from gui.impl.dialogs.sub_views.icon.icon_set import IconSet
from gui.impl.dialogs.sub_views.title.simple_text_title import SimpleTextTitle
from gui.impl.dialogs.sub_views.content.simple_text_content import SimpleTextContent
from gui.impl.gen import R
from gui.impl.gen.view_models.views.dialogs.default_dialog_place_holders import DefaultDialogPlaceHolders as Placeholder
from gui.impl.pub.dialog_window import DialogButtons
from gui.shared.gui_items.Tankman import getExtensionLessIconName, getDynIconName
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from uilogging.crew.logging_constants import CrewDialogKeys, CrewViewKeys

class SkinChangeDialog(BaseCrewDialogTemplateView):
    __slots__ = ('__tankmanInvID', '__initialData')
    LAYOUT_ID = R.views.lobby.crew.dialogs.DocumentChangeDialog()
    _INVALID_IDX = -1
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, tankmanInvID, ctx=None):
        super(SkinChangeDialog, self).__init__(loggingKey=CrewDialogKeys.DOCUMENT_CHANGE, parentViewKey=CrewViewKeys.PERSONAL_DATA)
        self.__tankmanInvID = tankmanInvID
        self.__initialData = ctx

    def _onLoading(self, *args, **kwargs):
        tankman = self._itemsCache.items.getTankman(self.__tankmanInvID)
        if tankman is None:
            self._setResult(DialogButtons.CANCEL)
            return
        else:
            self.setBackgroundImagePath(R.images.gui.maps.icons.crew.tankmanChangeAndRecruitView.bg())
            iconPath = R.images.gui.maps.icons.tankmen.icons.big
            if self.__initialData:
                iconData = self.__initialData.icon
                icon = getDynIconName(getExtensionLessIconName(tankman.nationID, iconData.id))
            else:
                icon = getDynIconName(tankman.extensionLessIcon)
            self.setSubView(Placeholder.ICON, IconSet(iconPath.dyn(icon)(), None, [R.images.gui.maps.icons.tankmen.windows.lipSmall_dialogs()]))
            self.setSubView(Placeholder.TITLE, SimpleTextTitle(str(backport.text(R.strings.dialogs.skinChangeDialog.title()))))
            self.setSubView(Placeholder.CONTENT, SimpleTextContent(str(backport.text(R.strings.dialogs.skinChangeDialog.text()))))
            self.addButton(ConfirmButton(R.strings.dialogs.skinChangeDialog.button.submit(), isDisabled=False))
            self.addButton(CancelButton())
            self.__updateSubmitBtnModel(not self.__initialData)
            super(SkinChangeDialog, self)._onLoading(*args, **kwargs)
            return

    def _getAdditionalData(self):
        return self.__initialData.icon if self.__initialData else None

    def __updateSubmitBtnModel(self, isDisabled=True):
        submitBtn = self.getButton(DialogButtons.SUBMIT)
        submitBtn.isDisabled = isDisabled
