# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/dialogs/gf_builders.py
import typing
from gui.impl.dialogs.dialog_template import DialogTemplateView
from gui.impl.dialogs.dialog_template_button import ButtonPresenter, CancelButton, ConfirmButton
from gui.impl.dialogs.dialog_template_utils import toString
from gui.impl.dialogs.sub_views.content.simple_text_content import SimpleTextContent
from gui.impl.dialogs.sub_views.icon.icon_set import IconSet
from gui.impl.dialogs.sub_views.title.simple_text_title import SimpleTextTitle
from gui.impl.dialogs.sub_views.top_right.money_balance import MoneyBalance
from gui.impl.gen import R
from gui.impl.gen.view_models.views.dialogs.default_dialog_place_holders import DefaultDialogPlaceHolders
from gui.impl.gen.view_models.views.dialogs.dialog_template_button_view_model import ButtonType
from gui.impl.gen_utils import DynAccessor
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogWindowWrapper
from gui.impl.pub.dialog_window import DialogButtons
if typing.TYPE_CHECKING:
    from typing import Optional, List, Union

class BaseDialogBuilder(object):
    __slots__ = ('__title', '__description', '__icon', '__buttons', '__uniqueID', '__backgroundID', '__backgroundDimmed', '__layoutID', '__selectedButtonID')

    def __init__(self, uniqueID=None):
        super(BaseDialogBuilder, self).__init__()
        self.__title = None
        self.__description = None
        self.__icon = None
        self.__buttons = []
        self.__uniqueID = uniqueID
        self.__backgroundID = None
        self.__backgroundDimmed = True
        self.__layoutID = None
        self.__selectedButtonID = None
        return

    def buildView(self):
        template = DialogTemplateView(layoutID=self.__layoutID, uniqueID=self.__uniqueID)
        if self.__title:
            template.setSubView(DefaultDialogPlaceHolders.TITLE, SimpleTextTitle(self.__title))
        if self.__description:
            template.setSubView(DefaultDialogPlaceHolders.CONTENT, SimpleTextContent(self.__description))
        if self.__icon:
            template.setSubView(DefaultDialogPlaceHolders.ICON, IconSet(*self.__icon))
        if self.__buttons:
            focusedButtonIndex = -1
            for index, buttonData in enumerate(self.__buttons):
                template.addButton(buttonData)
                if buttonData.buttonID == self.__selectedButtonID:
                    focusedButtonIndex = index

            template.setFocusedIndex(focusedButtonIndex)
        if self.__backgroundID:
            template.setBackgroundImagePath(self.__backgroundID)
        if not self.__backgroundDimmed:
            template.removeBackgroundDimmer()
        self._extendTemplate(template)
        return template

    def build(self):
        return FullScreenDialogWindowWrapper(self.buildView())

    def setTitle(self, text):
        self.__title = toString(text)

    def setDescription(self, text):
        self.__description = toString(text)

    def setIcon(self, mainIcon, backgrounds=None, overlays=None):
        self.__icon = (mainIcon, backgrounds, overlays)

    def addButton(self, buttonSettings):
        self.__buttons.append(buttonSettings)

    def getButton(self, buttonID):
        return next((data for data in self.__buttons if data.buttonID == buttonID))

    def setBackground(self, resourceID):
        self.__backgroundID = resourceID

    def setBackgroundDimmed(self, value=True):
        self.__backgroundDimmed = value

    def setLayoutID(self, layoutID):
        self.__layoutID = layoutID

    def setFocusedButtonID(self, buttonID):
        self.__selectedButtonID = buttonID

    def _extendTemplate(self, template):
        pass


class ResDialogBuilder(BaseDialogBuilder):
    __slots__ = ('__showBalance',)

    def __init__(self, uniqueID=None):
        super(ResDialogBuilder, self).__init__(uniqueID)
        self.__showBalance = False

    def setShowBalance(self, value):
        self.__showBalance = value

    def setMessagesAndButtons(self, message, buttons=R.strings.dialogs.common, focusedButtonID=DialogButtons.SUBMIT):
        self.setDescription(message.dyn('message')())
        self.setTitle(message.dyn('title')())
        for _id in DialogButtons.ALL:
            button = message.dyn(_id) or buttons.dyn(_id)
            if button.exists():
                self.addButton(ButtonPresenter(button(), _id, ButtonType.PRIMARY if _id == focusedButtonID else ButtonType.SECONDARY))

        self.setFocusedButtonID(focusedButtonID)

    def _extendTemplate(self, template):
        super(ResDialogBuilder, self)._extendTemplate(template)
        if self.__showBalance:
            template.setSubView(DefaultDialogPlaceHolders.TOP_RIGHT, MoneyBalance())


class ConfirmCancelDialogBuilder(BaseDialogBuilder):
    __slots__ = ()

    def __init__(self, uniqueID=None):
        super(ConfirmCancelDialogBuilder, self).__init__(uniqueID)
        self.addButton(ConfirmButton())
        self.setFocusedButtonID(DialogButtons.SUBMIT)
        self.addButton(CancelButton())

    def setConfirmButtonLabel(self, text):
        self.getButton(DialogButtons.SUBMIT).label = text

    def setCancelButtonLabel(self, text):
        self.getButton(DialogButtons.CANCEL).label = text


class AlertBuilder(BaseDialogBuilder):
    __slots__ = ()

    def __init__(self, uniqueID=None):
        super(AlertBuilder, self).__init__(uniqueID)
        self.addButton(ButtonPresenter(R.strings.dialogs.dialogTemplates.ok(), DialogButtons.CANCEL))
        self.setFocusedButtonID(DialogButtons.CANCEL)

    def setButtonLabel(self, text):
        self.getButton(DialogButtons.CANCEL).label = text


class InfoDialogBuilder(ConfirmCancelDialogBuilder):
    __slots__ = ()

    def __init__(self, uniqueID=None):
        super(InfoDialogBuilder, self).__init__(uniqueID)
        rDialogs = R.images.gui.maps.uiKit.dialogs
        self.setIcon(rDialogs.icons.info(), [rDialogs.highlights.blue()])


class WarningDialogBuilder(ConfirmCancelDialogBuilder):
    __slots__ = ()

    def __init__(self, uniqueID=None):
        super(WarningDialogBuilder, self).__init__(uniqueID)
        rDialogs = R.images.gui.maps.uiKit.dialogs
        self.setIcon(rDialogs.icons.alert(), [rDialogs.highlights.yellow_1()])


class ErrorAlertBuilder(AlertBuilder):
    __slots__ = ()

    def __init__(self, uniqueID=None):
        super(ErrorAlertBuilder, self).__init__(uniqueID)
        rDialogs = R.images.gui.maps.uiKit.dialogs
        self.setIcon(rDialogs.icons.error(), [rDialogs.highlights.red_1()])
