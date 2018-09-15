# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCPersonalCaseOberserver.py
import Event
from gui.Scaleform.daapi.view.meta.BCPersonalCaseObserverMeta import BCPersonalCaseObserverMeta

class BCPersonalCaseObserver(BCPersonalCaseObserverMeta):

    def __init__(self):
        super(BCPersonalCaseObserver, self).__init__()
        self.onSkillClickEvent = Event.Event()

    def onSkillClick(self, skillId):
        self.onSkillClickEvent(skillId)

    def _dispose(self):
        super(BCPersonalCaseObserver, self)._dispose()
        self.onSkillClickEvent.clear()
        self.onSkillClickEvent = None
        return
