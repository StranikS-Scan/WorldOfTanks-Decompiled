# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/dialogs/document_change_dialog.py
import operator
from base_crew_dialog_template_view import BaseCrewDialogTemplateView
from gui.impl import backport
from gui.impl.dialogs.dialog_template_button import CancelButton, ConfirmButton
from gui.impl.dialogs.sub_views.icon.icon_set import IconSet
from gui.impl.dialogs.sub_views.title.simple_text_title import SimpleTextTitle
from gui.impl.gen import R
from gui.impl.gen.view_models.views.dialogs.default_dialog_place_holders import DefaultDialogPlaceHolders as Placeholder
from gui.impl.gen.view_models.views.lobby.crew.dialogs.document_change_dialog_model import DocumentChangeDialogModel
from gui.impl.lobby.crew.utils import getDocGroupValues
from gui.impl.pub.dialog_window import DialogButtons
from gui.shared.gui_items.Tankman import getExtensionLessIconName, getDynIconName
from gui.shared.gui_items.items_actions import factory
from helpers import dependency
from items import tankmen
from skeletons.gui.shared import IItemsCache
from uilogging.crew.logging_constants import CrewDialogKeys, CrewViewKeys

class DocumentChangeDialog(BaseCrewDialogTemplateView):
    __slots__ = ('__tankmanInvID', '__initialData', '__firstNamesList', '__lastNamesList', '__firstNameIdx', '__lastNameIdx')
    LAYOUT_ID = R.views.lobby.crew.dialogs.DocumentChangeDialog()
    VIEW_MODEL = DocumentChangeDialogModel
    _INVALID_IDX = -1
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, tankmanInvID, ctx=None):
        super(DocumentChangeDialog, self).__init__(loggingKey=CrewDialogKeys.DOCUMENT_CHANGE, parentViewKey=CrewViewKeys.PERSONAL_DATA)
        self.__tankmanInvID = tankmanInvID
        self.__initialData = ctx
        self.__firstNamesList = []
        self.__lastNamesList = []
        self.__firstNameIdx = self._INVALID_IDX
        self.__lastNameIdx = self._INVALID_IDX

    @property
    def viewModel(self):
        return self.getViewModel()

    def _getEvents(self):
        return ((self.viewModel.onChangeFirstName, self._onChangeFirstName), (self.viewModel.onChangeLastName, self._onChangeLastName))

    def _onLoading(self, *args, **kwargs):
        tankman = self._itemsCache.items.getTankman(self.__tankmanInvID)
        if tankman is None:
            self._setResult(DialogButtons.CANCEL)
        self.setBackgroundImagePath(R.images.gui.maps.icons.windows.background())
        iconPath = R.images.gui.maps.icons.tankmen.icons.big
        if self.__initialData:
            iconData = self.__initialData.icon
            icon = getDynIconName(getExtensionLessIconName(tankman.nationID, iconData.id))
        else:
            icon = getDynIconName(tankman.extensionLessIcon)
        self.setSubView(Placeholder.ICON, IconSet(iconPath.dyn(icon)(), None, [R.images.gui.maps.icons.tankmen.windows.lipSmall_dialogs()]))
        self.setSubView(Placeholder.TITLE, SimpleTextTitle(str(backport.text(R.strings.dialogs.documentChangeDialog.title()))))
        self.addButton(ConfirmButton(R.strings.dialogs.documentChangeDialog.button.submit(), isDisabled=True))
        self.addButton(CancelButton())
        self._updateViewModel(tankman)
        super(DocumentChangeDialog, self)._onLoading(*args, **kwargs)
        return

    def _updateViewModel(self, tankman):
        config = tankmen.getNationConfig(tankman.nationID)
        self.__firstNamesList = getDocGroupValues(tankman, config, operator.attrgetter('firstNamesList'), config.getFirstName)
        self.__lastNamesList = getDocGroupValues(tankman, config, operator.attrgetter('lastNamesList'), config.getLastName)
        with self.viewModel.transaction() as vm:
            if self.__initialData:
                firstName, lastName = self.__initialData.firstName.value, self.__initialData.lastName.value
                self.__updateSubmitBtnModel(firstName == tankman.firstUserName and lastName == tankman.lastUserName)
            else:
                firstName, lastName = tankman.firstUserName, tankman.lastUserName
                self.__updateSubmitBtnModel(not tankman.isInSkin)
            self.__firstNameIdx = self.__fillItemsList(vm.getFirstNameList(), self.__firstNamesList, firstName, self._INVALID_IDX)
            self.__lastNameIdx = self.__fillItemsList(vm.getLastNameList(), self.__lastNamesList, lastName, self._INVALID_IDX)
            vm.setFirstNameIndex(self.__firstNameIdx)
            vm.setLastNameIndex(self.__lastNameIdx)

    def _onChangeFirstName(self, args):
        with self.viewModel.transaction() as vm:
            vm.setFirstNameIndex(args.get('index'))
        self.__updateSubmitBtnModel(not self.__updateSelectionIdxs())

    def _onChangeLastName(self, args):
        with self.viewModel.transaction() as vm:
            vm.setLastNameIndex(args.get('index'))
        self.__updateSubmitBtnModel(not self.__updateSelectionIdxs())

    def _setResult(self, result):
        if result == DialogButtons.SUBMIT:
            firstNameID = firstNameGroup = lastNameID = lastNameGroup = iconID = iconGroup = self._INVALID_IDX
            if 0 <= self.__firstNameIdx < len(self.__firstNamesList):
                firstNameID, firstNameGroup, _ = self.__firstNamesList[self.__firstNameIdx]
            if 0 <= self.__lastNameIdx < len(self.__lastNamesList):
                lastNameID, lastNameGroup, _ = self.__lastNamesList[self.__lastNameIdx]
            if self.__initialData:
                iconData = self.__initialData.icon
                iconID = iconData.id if iconData.id is not None else self._INVALID_IDX
                iconGroup = iconData.group if iconData.group is not None else self._INVALID_IDX
            factory.doAction(factory.CHANGE_TANKMAN_PASSPORT, self.__tankmanInvID, firstNameID, firstNameGroup, lastNameID, lastNameGroup, iconID, iconGroup)
        super(DocumentChangeDialog, self)._setResult(result)
        return

    def __updateSelectionIdxs(self):
        if self.viewModel.getFirstNameIndex() != self.__firstNameIdx or self.viewModel.getLastNameIndex() != self.__lastNameIdx:
            self.__firstNameIdx = self.viewModel.getFirstNameIndex()
            self.__lastNameIdx = self.viewModel.getLastNameIndex()
            return True
        return False

    def __updateSubmitBtnModel(self, isDisabled=True):
        submitBtn = self.getButton(DialogButtons.SUBMIT)
        submitBtn.isDisabled = isDisabled

    @staticmethod
    def __fillItemsList(vm, itemList, selectedItemName, selectedIdx):
        vm.clear()
        for idx, itemData in enumerate(itemList):
            _, _, nameStr = itemData
            if selectedItemName == nameStr:
                selectedIdx = idx
            vm.addString(nameStr)

        vm.invalidate()
        return selectedIdx
