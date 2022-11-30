# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/dialogs/challenge/buy_celebrity_quest_item_dialog_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_resource_model import NyResourceModel

class DialogState(Enum):
    ERROR = 'error'
    NOWALLET = 'noWallet'
    NOTENOUGHMONEY = 'notEnoughMoney'
    DEFAULT = 'default'


class ResourceType(Enum):
    CRYSTAL = 'ny_crystal'
    EMERALD = 'ny_emerald'
    AMBER = 'ny_amber'
    IRON = 'ny_iron'


class BuyCelebrityQuestItemDialogModel(ViewModel):
    __slots__ = ('onAccept', 'onCancel')

    def __init__(self, properties=6, commands=2):
        super(BuyCelebrityQuestItemDialogModel, self).__init__(properties=properties, commands=commands)

    def getResources(self):
        return self._getArray(0)

    def setResources(self, value):
        self._setArray(0, value)

    @staticmethod
    def getResourcesType():
        return NyResourceModel

    def getDialogState(self):
        return DialogState(self._getString(1))

    def setDialogState(self, value):
        self._setString(1, value.value)

    def getQuestId(self):
        return self._getString(2)

    def setQuestId(self, value):
        self._setString(2, value)

    def getPrice(self):
        return self._getNumber(3)

    def setPrice(self, value):
        self._setNumber(3, value)

    def getResourceType(self):
        return ResourceType(self._getString(4))

    def setResourceType(self, value):
        self._setString(4, value.value)

    def getIsMaxAtmosphereLevel(self):
        return self._getBool(5)

    def setIsMaxAtmosphereLevel(self, value):
        self._setBool(5, value)

    def _initialize(self):
        super(BuyCelebrityQuestItemDialogModel, self)._initialize()
        self._addArrayProperty('resources', Array())
        self._addStringProperty('dialogState')
        self._addStringProperty('questId', '')
        self._addNumberProperty('price', 0)
        self._addStringProperty('resourceType')
        self._addBoolProperty('isMaxAtmosphereLevel', False)
        self.onAccept = self._addCommand('onAccept')
        self.onCancel = self._addCommand('onCancel')
