# Embedded file name: scripts/client/tutorial/gui/Scaleform/pop_ups.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from tutorial.control import TutorialProxyHolder
from tutorial.data.events import ClickEvent
from tutorial.gui import GUI_EFFECT_NAME
from tutorial.gui.Scaleform.meta.TutorialDialogMeta import TutorialDialogMeta
from tutorial.logger import LOG_ERROR
from gui.Scaleform.locale.BATTLE_TUTORIAL import BATTLE_TUTORIAL
from helpers import i18n

class TutorialPopUp(AbstractWindowView, TutorialProxyHolder):

    def __init__(self, content):
        super(TutorialPopUp, self).__init__()
        self._content = content

    def _onMouseClicked(self, targetKey):
        if targetKey in self._content:
            targetID = self._content[targetKey]
            if len(targetID):
                self._gui.onGUIInput(ClickEvent(targetID))
            else:
                LOG_ERROR('ID of target is empty', targetKey)
        else:
            LOG_ERROR('Target not found in data', targetKey)


class TutorialDialog(TutorialPopUp, TutorialDialogMeta):

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


class TutorialQueueDialog(TutorialDialog):

    def _populate(self):
        super(TutorialQueueDialog, self)._populate()
        data = self._content
        pointcuts = data['timePointcuts']
        firstPntCut = pointcuts[0]
        lastPntCut = pointcuts[len(pointcuts) - 1]
        self.as_setContentS({'title': data['title'],
         'message': data['message'],
         'playerTimeTextStart': data['playerTimeTextStart'],
         'playerTimeTextEnd': data['playerTimeTextEnd'],
         'avgTimeText': data['avgTimeText'],
         'updatePeriod': 60,
         'timePointcuts': {'firstPointcut': {'value': firstPntCut,
                                             'text': i18n.makeString(BATTLE_TUTORIAL.LABELS_LESS_N_MINUTES, minutes=firstPntCut)},
                           'lastPointcut': {'value': lastPntCut,
                                            'text': i18n.makeString(BATTLE_TUTORIAL.LABELS_MORE_N_MINUTES, minutes=lastPntCut)},
                           'betweenPointcutsTextAlias': BATTLE_TUTORIAL.LABELS_MINUTES}})

    def as_updateContentS(self, data):
        return super(TutorialQueueDialog, self).as_updateContentS({'avgTimeText': data['avgTimeText']})


class TutorialGreetingDialog(TutorialDialog):

    def _populate(self):
        super(TutorialGreetingDialog, self)._populate()
        data = self._content
        self.as_setContentS({'message': data['message'],
         'imageUrl': data['imageUrl'],
         'timeNoteValue': data['timeNoteValue'],
         'bonuses': data['bonuses']})


class TutorialWindow(TutorialPopUp):

    def _stop(self):
        self._content.clear()
        self._gui.effects.stop(GUI_EFFECT_NAME.SHOW_WINDOW, effectID=self.uniqueName)

    def onWindowClose(self):
        self._onMouseClicked('closeID')
        self._stop()
