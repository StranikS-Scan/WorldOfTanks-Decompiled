# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/TrainingWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class TrainingWindowMeta(AbstractWindowView):

    def getInfo(self):
        self._printOverrideError('getInfo')

    def getMapsData(self):
        self._printOverrideError('getMapsData')

    def updateTrainingRoom(self, key, time, isPrivate, description):
        self._printOverrideError('updateTrainingRoom')
