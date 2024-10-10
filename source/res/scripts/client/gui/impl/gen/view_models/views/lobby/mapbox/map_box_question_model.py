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
    MULTIPLE_CHOICE = 'multipleChoice'
    BIG_PICTURE = 'bigPicture'


class MapBoxQuestionModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(MapBoxQuestionModel, self).__init__(properties=properties, commands=commands)

    @property
    def answers(self):
        return self._getViewModel(0)

    @staticmethod
    def getAnswersType():
        return MapBoxAnswersModel

    @property
    def options(self):
        return self._getViewModel(1)

    @staticmethod
    def getOptionsType():
        return MapBoxOptionModel

    def getType(self):
        return QuestionType(self._getString(2))

    def setType(self, value):
        self._setString(2, value.value)

    def getImagePath(self):
        return self._getString(3)

    def setImagePath(self, value):
        self._setString(3, value)

    def getPathPrefix(self):
        return self._getString(4)

    def setPathPrefix(self, value):
        self._setString(4, value)

    def getShowIcons(self):
        return self._getBool(5)

    def setShowIcons(self, value):
        self._setBool(5, value)

    def getQuestionId(self):
        return self._getString(6)

    def setQuestionId(self, value):
        self._setString(6, value)

    def getTitleParams(self):
        return self._getArray(7)

    def setTitleParams(self, value):
        self._setArray(7, value)

    @staticmethod
    def getTitleParamsType():
        return unicode

    def _initialize(self):
        super(MapBoxQuestionModel, self)._initialize()
        self._addViewModelProperty('answers', MapBoxAnswersModel())
        self._addViewModelProperty('options', UserListModel())
        self._addStringProperty('type')
        self._addStringProperty('imagePath', '')
        self._addStringProperty('pathPrefix', '')
        self._addBoolProperty('showIcons', False)
        self._addStringProperty('questionId', '')
        self._addArrayProperty('titleParams', Array())
