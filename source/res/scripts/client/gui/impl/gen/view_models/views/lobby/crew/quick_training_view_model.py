# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/quick_training_view_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.crew.common.base_crew_view_model import BaseCrewViewModel
from gui.impl.gen.view_models.views.lobby.crew.common.info_tip_model import InfoTipModel
from gui.impl.gen.view_models.views.lobby.crew.freeXp_book_model import FreeXpBookModel
from gui.impl.gen.view_models.views.lobby.crew.learning_data_model import LearningDataModel
from gui.impl.gen.view_models.views.lobby.crew.training_book_model import TrainingBookModel

class QuickTrainingViewModel(BaseCrewViewModel):
    __slots__ = ('onLearn', 'onCancel', 'onBuyBook', 'onTipClose', 'onCardMouseLeave', 'onFreeXpMouseEnter', 'onFreeXpSelected', 'onFreeXpUpdated', 'onFreeXpManualInput', 'onBookMouseEnter', 'onBookSelected')

    def __init__(self, properties=9, commands=15):
        super(QuickTrainingViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def freeXpData(self):
        return self._getViewModel(2)

    @staticmethod
    def getFreeXpDataType():
        return FreeXpBookModel

    @property
    def learningData(self):
        return self._getViewModel(3)

    @staticmethod
    def getLearningDataType():
        return LearningDataModel

    def getNationName(self):
        return self._getString(4)

    def setNationName(self, value):
        self._setString(4, value)

    def getVehicleName(self):
        return self._getString(5)

    def setVehicleName(self, value):
        self._setString(5, value)

    def getTankmanName(self):
        return self._getString(6)

    def setTankmanName(self, value):
        self._setString(6, value)

    def getBooksList(self):
        return self._getArray(7)

    def setBooksList(self, value):
        self._setArray(7, value)

    @staticmethod
    def getBooksListType():
        return TrainingBookModel

    def getTips(self):
        return self._getArray(8)

    def setTips(self, value):
        self._setArray(8, value)

    @staticmethod
    def getTipsType():
        return InfoTipModel

    def _initialize(self):
        super(QuickTrainingViewModel, self)._initialize()
        self._addViewModelProperty('freeXpData', FreeXpBookModel())
        self._addViewModelProperty('learningData', LearningDataModel())
        self._addStringProperty('nationName', '')
        self._addStringProperty('vehicleName', '')
        self._addStringProperty('tankmanName', '')
        self._addArrayProperty('booksList', Array())
        self._addArrayProperty('tips', Array())
        self.onLearn = self._addCommand('onLearn')
        self.onCancel = self._addCommand('onCancel')
        self.onBuyBook = self._addCommand('onBuyBook')
        self.onTipClose = self._addCommand('onTipClose')
        self.onCardMouseLeave = self._addCommand('onCardMouseLeave')
        self.onFreeXpMouseEnter = self._addCommand('onFreeXpMouseEnter')
        self.onFreeXpSelected = self._addCommand('onFreeXpSelected')
        self.onFreeXpUpdated = self._addCommand('onFreeXpUpdated')
        self.onFreeXpManualInput = self._addCommand('onFreeXpManualInput')
        self.onBookMouseEnter = self._addCommand('onBookMouseEnter')
        self.onBookSelected = self._addCommand('onBookSelected')
