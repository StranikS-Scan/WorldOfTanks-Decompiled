# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/ui/maps_training.py
from helpers import dependency
from skeletons.gui.game_control import IMapsTrainingController
from web.web_client_api import w2c, W2CSchema

class OpenMapsTrainingMixin(object):
    mapsTrainingController = dependency.descriptor(IMapsTrainingController)

    @w2c(W2CSchema, 'maps_training')
    def selectMapsTrainingMode(self, _):
        if self.mapsTrainingController.isMapsTrainingEnabled:
            self.mapsTrainingController.selectMapsTrainingMode()
