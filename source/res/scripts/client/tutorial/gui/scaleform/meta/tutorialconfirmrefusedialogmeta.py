# Embedded file name: scripts/client/tutorial/gui/Scaleform/meta/TutorialConfirmRefuseDialogMeta.py
from tutorial.gui.Scaleform.pop_ups import TutorialDialog

class TutorialConfirmRefuseDialogMeta(TutorialDialog):

    def setStartOnNextLogin(self, vaule):
        self._printOverrideError('setStartOnNextLogin')
