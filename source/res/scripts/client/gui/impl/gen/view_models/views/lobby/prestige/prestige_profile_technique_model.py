# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/prestige/prestige_profile_technique_model.py
from gui.impl.gen.view_models.views.lobby.prestige.prestige_base_model import PrestigeBaseModel
from gui.impl.gen.view_models.views.lobby.prestige.prestige_emblem_model import PrestigeEmblemModel

class PrestigeProfileTechniqueModel(PrestigeBaseModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(PrestigeProfileTechniqueModel, self).__init__(properties=properties, commands=commands)

    @property
    def nextEmblem(self):
        return self._getViewModel(3)

    @staticmethod
    def getNextEmblemType():
        return PrestigeEmblemModel

    def _initialize(self):
        super(PrestigeProfileTechniqueModel, self)._initialize()
        self._addViewModelProperty('nextEmblem', PrestigeEmblemModel())
