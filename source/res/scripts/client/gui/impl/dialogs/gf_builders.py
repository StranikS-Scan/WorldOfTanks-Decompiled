# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/dialogs/gf_builders.py
import typing
from frameworks.wulf import WindowLayer
from gui.impl.dialogs.dialog_template import DialogTemplateView, DEFAULT_DIMMER_ALPHA
from gui.impl.dialogs.sub_views.common.simple_text import ImageSubstitution
from gui.impl.dialogs.sub_views.content.text_warning_content import TextWithWarning
from gui.impl.dialogs.dialog_template_button import ButtonPresenter, CancelButton, ConfirmButton
from gui.impl.dialogs.dialog_template_utils import toString
from gui.impl.dialogs.sub_views.content.simple_text_content import SimpleTextContent
from gui.impl.dialogs.sub_views.icon.icon_set import IconSet
from gui.impl.dialogs.sub_views.title.simple_text_title import SimpleTextTitle
from gui.impl.dialogs.sub_views.top_right.money_balance import MoneyBalance
from gui.impl.gen import R
from gui.impl.gen.view_models.views.dialogs.default_dialog_place_holders import DefaultDialogPlaceHolders
from gui.impl.gen.view_models.views.dialogs.sub_views.icon_set_view_model import IconPositionLogicEnum
from gui.impl.gen.view_models.views.dialogs.dialog_template_button_view_model import ButtonType
from gui.impl.gen_utils import DynAccessor
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogWindowWrapper
from gui.impl.pub.dialog_window import DialogButtons
if typing.TYPE_CHECKING:
    from typing import Optional, List, Union

class BuilderDialogTemplateView(DialogTemplateView):
    __slots__ = ()

    def _closeClickHandler(self, args=None):
        reason = (args or {}).get('reason')
        self._setResult(reason or DialogButtons.CANCEL)


class BaseDialogBuilder(object):
    __slots__ = ('__title', '__description', '__icon', '__buttons', '__uniqueID', '__backgroundID', '__dimmerAlpha', '__layoutID', '__selectedButtonID', '__doBlur', '__layer', '__displayFlags', '__descriptionImageSubstitutions', '__titleImageSubstitutions')

    def __init__(self, uniqueID=None):
        super(BaseDialogBuilder, self).__init__()
        self.__title = None
        self.__titleImageSubstitutions = None
        self.__description = None
        self.__descriptionImageSubstitutions = None
        self.__icon = None
        self.__buttons = []
        self.__uniqueID = uniqueID
        self.__backgroundID = None
        self.__dimmerAlpha = DEFAULT_DIMMER_ALPHA
        self.__layoutID = None
        self.__selectedButtonID = None
        self.__doBlur = True
        self.__layer = WindowLayer.UNDEFINED
        self.__displayFlags = []
        return

    def buildView(self):
        template = BuilderDialogTemplateView(layoutID=self.__layoutID, uniqueID=self.__uniqueID)
        if self.__title:
            template.setSubView(DefaultDialogPlaceHolders.TITLE, SimpleTextTitle(self.__title, self.__titleImageSubstitutions))
        if self.__description:
            template.setSubView(DefaultDialogPlaceHolders.CONTENT, SimpleTextContent(self.__description, self.__descriptionImageSubstitutions))
        if self.__icon:
            template.setSubView(DefaultDialogPlaceHolders.ICON, IconSet(**self.__icon))
        if self.__buttons:
            focusedButtonIndex = -1
            for index, buttonData in enumerate(self.__buttons):
                template.addButton(buttonData)
                if buttonData.buttonID == self.__selectedButtonID:
                    focusedButtonIndex = index

            template.setFocusedIndex(focusedButtonIndex)
        if self.__backgroundID:
            template.setBackgroundImagePath(self.__backgroundID)
        template.setBackgroundDimmerAlpha(self.__dimmerAlpha)
        if self.__displayFlags:
            template.setDisplayFlags(*self.__displayFlags)
        self._extendTemplate(template)
        return template

    def build(self):
        return FullScreenDialogWindowWrapper(self.buildView(), doBlur=self.__doBlur, layer=self.__layer)

    def setTitle(self, text, imageSubstitutions=None):
        self.__title = toString(text)
        if imageSubstitutions:
            self.__titleImageSubstitutions = imageSubstitutions

    def setDescription(self, text, imageSubstitutions=None):
        self.__description = toString(text)
        if imageSubstitutions:
            self.__descriptionImageSubstitutions = imageSubstitutions

    def setIcon(self, mainIcon, backgrounds=None, overlays=None, layoutID=None, iconPositionLogic=IconPositionLogicEnum.CENTREDANDTHROUGHCONTENT.value):
        self.__icon = {'iconResID': mainIcon,
         'backgroundResIDList': backgrounds,
         'overlayResIDList': overlays,
         'layoutID': layoutID,
         'iconPositionLogic': iconPositionLogic}

    def addButton(self, buttonSettings):
        self.__buttons.append(buttonSettings)

    def getButton(self, buttonID):
        return next((data for data in self.__buttons if data.buttonID == buttonID))

    def setBackground(self, resourceID):
        self.__backgroundID = resourceID

    def setDimmerAlpha(self, value):
        self.__dimmerAlpha = value

    def setLayoutID(self, layoutID):
        self.__layoutID = layoutID

    def setFocusedButtonID(self, buttonID):
        self.__selectedButtonID = buttonID

    def setBlur(self, value=True):
        self.__doBlur = value

    def setLayer(self, layerID):
        self.__layer = layerID

    def setDisplayFlags(self, *displayFlags):
        self.__displayFlags = displayFlags

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


class ConfirmCancelWarningDialogBuilder(ConfirmCancelDialogBuilder):
    __slots__ = ('__descriptionMsg', '__warningMsg')

    def __init__(self, uniqueID=None):
        super(ConfirmCancelWarningDialogBuilder, self).__init__(uniqueID)
        self.__descriptionMsg = None
        self.__warningMsg = None
        return

    def setDescription(self, text):
        pass

    def setDescriptionMsg(self, text):
        self.__descriptionMsg = toString(text)

    def setWarningMsg(self, text):
        self.__warningMsg = toString(text)

    def _extendTemplate(self, template):
        super(ConfirmCancelWarningDialogBuilder, self)._extendTemplate(template)
        if self.__descriptionMsg and self.__warningMsg:
            template.setSubView(DefaultDialogPlaceHolders.CONTENT, TextWithWarning(self.__descriptionMsg, self.__warningMsg))


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


class AcceleratedCrewTrainingDialogBuilder(ConfirmCancelDialogBuilder):
    __slots__ = ()

    def __init__(self, uniqueID=None):
        super(AcceleratedCrewTrainingDialogBuilder, self).__init__(uniqueID)
        self.setIcon(R.images.gui.maps.uiKit.dialogs.icons.accelerated_crew())


class PassiveXPDialogBuilder(ConfirmCancelDialogBuilder):
    __slots__ = ('__descriptionMsg', '__icon')

    def __init__(self, uniqueID=None):
        super(PassiveXPDialogBuilder, self).__init__(uniqueID)
        self.setIcon(R.images.gui.maps.uiKit.dialogs.icons.intensive_crew())
        self.__descriptionMsg = None
        self.__icon = None
        return

    def setDescriptionMsg(self, text):
        self.__descriptionMsg = text

    def setMessageIcon(self, icon):
        self.__icon = icon

    def _extendTemplate(self, template):
        super(PassiveXPDialogBuilder, self)._extendTemplate(template)
        if self.__descriptionMsg and self.__icon:
            image = ImageSubstitution(self.__icon(), 'typeIcon', 3, -5, -5, -5)
            template.setSubView(DefaultDialogPlaceHolders.CONTENT, SimpleTextContent(self.__descriptionMsg, imageSubstitutions=[image]))


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
