# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/dialogs/event_afk_dialog.py
import typing
from gui import makeHtmlString
from gui.Scaleform.daapi.view.dialogs import DIALOG_BUTTON_ID, I18nDialogMeta, I18nInfoDialogButtons, I18nConfirmDialogButtons
from gui.Scaleform.daapi.view.lobby.event_boards.formaters import formatTimeAndDate
from gui.Scaleform.daapi.view.meta.EventAFKDialogMeta import EventAFKDialogMeta
from gui.shared.events import ShowDialogEvent
from helpers import dependency
from skeletons.gui.afk_controller import IAFKController
if typing.TYPE_CHECKING:
    from typing import Callable

class EventAFKDialogMetaData(I18nDialogMeta):
    _HTML_TAG = 'html_templates:lobby/dialogs/eventAFK/'
    BATTLE_WARNING = 'event/afk/battle'
    AFTER_BATTLE_WARNING = 'event/afk/afterBattle'
    BAN_MESSAGE = 'event/afk/ban'

    def __init__(self, key):
        super(EventAFKDialogMetaData, self).__init__(key, buttons=self.__getButtons(key), messageCtx=self.__getMessageCtx(key))

    def getImagePath(self):
        return '../maps/icons/event/afkMessageDialog/ban.png' if self._key == self.BAN_MESSAGE else '../maps/icons/event/afkMessageDialog/warning.png'

    def getEventType(self):
        return ShowDialogEvent.SHOW_EVENT_AFK_DIALOG

    def __getMessageCtx(self, key):
        ctx = {'subTitleOpenTag': makeHtmlString(self._HTML_TAG, 'subTitleOpenTag'),
         'closeTag': makeHtmlString(self._HTML_TAG, 'closeTag'),
         'indent': makeHtmlString(self._HTML_TAG, 'indent')}
        if key == self.BAN_MESSAGE:
            afkController = dependency.instance(IAFKController)
            date = afkController.banExpiryTime
            dateFormatted = formatTimeAndDate(date)
            ctx.update({'pardonDate': dateFormatted})
        return ctx

    def __getButtons(self, key):
        return I18nInfoDialogButtons(key) if key == self.AFTER_BATTLE_WARNING else I18nConfirmDialogButtons(key, DIALOG_BUTTON_ID.CLOSE)


class EventAFKDialog(EventAFKDialogMeta):

    def __init__(self, meta, handler):
        super(EventAFKDialog, self).__init__(meta.getMessage(), meta.getTitle(), meta.getButtonLabels(), meta.getCallbackWrapper(handler))
        self.__imagePath = meta.getImagePath()

    def _populate(self):
        super(EventAFKDialog, self)._populate()
        self.as_setDataS(self.__imagePath)
