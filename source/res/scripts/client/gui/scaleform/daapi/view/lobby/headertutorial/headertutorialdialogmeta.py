# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/headerTutorial/HeaderTutorialDialogMeta.py
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogMeta
from gui.shared import events

class RefuseHeaderTutorialDialogMeta(I18nConfirmDialogMeta):

    def __init__(self):
        super(RefuseHeaderTutorialDialogMeta, self).__init__('headerTutorialDialog')

    def getEventType(self):
        return events.ShowDialogEvent.SHOW_HEADER_TUTORIAL_DIALOG
