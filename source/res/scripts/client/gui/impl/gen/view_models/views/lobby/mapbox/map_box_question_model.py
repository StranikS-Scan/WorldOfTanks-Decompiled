# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/mapbox/map_box_question_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.mapbox.map_box_answers_model import MapBoxAnswersModel
from gui.impl.gen.view_models.views.lobby.mapbox.map_box_option_model import MapBoxOptionModel

class QuestionType(Enum):
    VEHICLE = 'vehicle'
    IMAGE = 'image'
    TABLE = 'table'
    INTERACTIVE_MAP = 'interactiveMap'
    TEXT = 'text'
    UNDEFINED = 'undefined'
    ALTERNATIVE = 'alternative'


class MapBoxQuestionModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(MapBoxQuestionModel, self).__init__(properties=properties, commands=commands)

    @property
    def answers(self):
        return self._getViewModel(0)

    @property
    def options(self):
        return self._getViewModel(1)

    def getType(self):
        return QuestionType(self._getString(2))

    def setType(self, value):
        self._setString(2, value.value)

    def getImagePath(self):
        return self._getString(3)

    def setImagePath(self, value):
        self._setString(3, value)

    def getShowIcons(self):
        return self._getBool(4)

    def setShowIcons(self, value):
        self._setBool(4, value)

    def getQuestionId(self):
        return self._getString(5)

    def setQuestionId(self, value):
        self._setString(5, value)

    def getTitleParams(self):
        return self._getArray(6)

    def setTitleParams(self, value):
        self._setArray(6, value)

    def _initialize(self):
        super(MapBoxQuestionModel, self)._initialize()
        self._addViewModelProperty('answers', MapBoxAnswersModel())
        self._addViewModelProperty('options', UserListModel())
        self._addStringProperty('type')
        self._addStringProperty('imagePath', '')
        self._addBoolProperty('showIcons', False)
        self._addStringProperty('questionId', '')
        self._addArrayProperty('titleParams', Array())
