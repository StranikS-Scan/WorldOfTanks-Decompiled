# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/dialogs/bootcamp_dialogs_meta.py
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogMeta
from gui.Scaleform.locale.BATTLE_TUTORIAL import BATTLE_TUTORIAL
from gui.shared.events import ShowDialogEvent
from helpers import i18n

class ExecutionChooserDialogMeta(I18nConfirmDialogMeta):
    SKIP = 'skip'
    RETRY = 'retry'
    START = 'start'

    def __init__(self, dialogType, key, focusedID, showAwardIcon):
        super(ExecutionChooserDialogMeta, self).__init__(key, focusedID=focusedID)
        self.__imagePath = '../maps/icons/bootcamp/dialog/%s.png' % dialogType
        self.__showAwardIcon = showAwardIcon

    def getEventType(self):
        return ShowDialogEvent.SHOW_EXECUTION_CHOOSER_DIALOG

    def getImagePath(self):
        return self.__imagePath

    def getShowAwardIcon(self):
        return self.__showAwardIcon

    def getAwardingText(self):
        return i18n.makeString(BATTLE_TUTORIAL.LABELS_BONUSES_ALREADY_RECEIVED, **self._messageCtx)

    def getLabel(self):
        I18N_LABEL_KEY = '{0:>s}/label'
        return self._makeString(I18N_LABEL_KEY.format(self._key), self._messageCtx)
