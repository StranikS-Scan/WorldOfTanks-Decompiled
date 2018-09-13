# Embedded file name: scripts/client/tutorial/gui/Scaleform/pop_ups.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.framework.entities.View import View
from tutorial.control import TutorialProxyHolder
from tutorial.gui import GUIEvent, GUI_EFFECT_NAME
from tutorial.gui.Scaleform.meta.TutorialDialogMeta import TutorialDialogMeta
from tutorial.logger import LOG_ERROR

class TutorialPopUp(View, AbstractWindowView, TutorialProxyHolder):

    def __init__(self, content):
        super(TutorialPopUp, self).__init__()
        self._content = content

    def _onMouseClicked(self, targetKey):
        if targetKey in self._content:
            targetID = self._content[targetKey]
            if len(targetID):
                self._gui.onMouseClicked(GUIEvent('MouseEvent', targetID))
            else:
                LOG_ERROR('ID of target is empty', targetKey)
        else:
            LOG_ERROR('Target not found in data', targetKey)


class TutorialDialog(TutorialPopUp, TutorialDialogMeta):

    def _populate(self):
        super(TutorialDialog, self)._populate()
        self.as_setContentS(self._content.copy())

    def _stop(self):
        self._content.clear()
        self._gui.effects.stop(GUI_EFFECT_NAME.SHOW_DIALOG, effectID=self.uniqueName)

    def submit(self):
        self._onMouseClicked('submitID')
        self._stop()

    def cancel(self):
        self._onMouseClicked('cancelID')
        self._stop()

    def onWindowClose(self):
        self.cancel()


class TutorialWindow(TutorialPopUp):

    def _stop(self):
        self._content.clear()
        self._gui.effects.stop(GUI_EFFECT_NAME.SHOW_WINDOW, effectID=self.uniqueName)

    def onWindowClose(self):
        self._onMouseClicked('closeID')
        self._stop()
