# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/container_vews/skills_training/events.py
from gui.impl.lobby.container_views.base.events import ComponentEventsBase

class SkillsTrainingComponentViewEvents(ComponentEventsBase):

    def __init__(self):
        super(SkillsTrainingComponentViewEvents, self).__init__()
        self.onSkillHover = self._createEvent()
        self.onSkillOut = self._createEvent()
        self.onSkillClick = self._createEvent()
        self.onTrain = self._createEvent()
        self.onCancel = self._createEvent()
        self.onClose = self._createEvent()
