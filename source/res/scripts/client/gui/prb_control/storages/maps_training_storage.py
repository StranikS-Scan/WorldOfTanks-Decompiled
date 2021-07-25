# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/storages/maps_training_storage.py
from gui.prb_control.storages.local_storage import SessionStorage
from helpers import dependency
from skeletons.gui.game_control import IMapsTrainingController

class MapsTrainingStorage(SessionStorage):
    mapsTrainingController = dependency.descriptor(IMapsTrainingController)

    def isModeSelected(self):
        return super(MapsTrainingStorage, self).isModeSelected() and self.mapsTrainingController.isMapsTrainingEnabled

    def _determineSelection(self, arenaVisitor):
        return arenaVisitor.gui.isMapsTraining()
