# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/mapbox/map_box_option_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.mapbox.map_box_answers_model import MapBoxAnswersModel

class MapBoxOptionModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(MapBoxOptionModel, self).__init__(properties=properties, commands=commands)

    @property
    def answers(self):
        return self._getViewModel(0)

    def getOptionId(self):
        return self._getString(1)

    def setOptionId(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(MapBoxOptionModel, self)._initialize()
        self._addViewModelProperty('answers', MapBoxAnswersModel())
        self._addStringProperty('optionId', '')
