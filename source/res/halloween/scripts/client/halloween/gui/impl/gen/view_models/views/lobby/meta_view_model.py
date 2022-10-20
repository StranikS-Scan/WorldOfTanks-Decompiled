# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/lobby/meta_view_model.py
from frameworks.wulf import Array
from halloween.gui.impl.gen.view_models.views.lobby.common.base_quest_model import BaseQuestModel
from halloween.gui.impl.gen.view_models.views.lobby.common.base_view_model import BaseViewModel
from halloween.gui.impl.gen.view_models.views.lobby.witches_model import WitchesModel

class MetaViewModel(BaseViewModel):
    __slots__ = ('onInfoClick', 'onAboutClick', 'onPreviewClick', 'onShopClick', 'onPhaseChange')

    def __init__(self, properties=7, commands=6):
        super(MetaViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def witchesWidget(self):
        return self._getViewModel(2)

    @staticmethod
    def getWitchesWidgetType():
        return WitchesModel

    def getIsViewHidden(self):
        return self._getBool(3)

    def setIsViewHidden(self, value):
        self._setBool(3, value)

    def getIsNew(self):
        return self._getBool(4)

    def setIsNew(self, value):
        self._setBool(4, value)

    def getAbilityIconName(self):
        return self._getString(5)

    def setAbilityIconName(self, value):
        self._setString(5, value)

    def getQuests(self):
        return self._getArray(6)

    def setQuests(self, value):
        self._setArray(6, value)

    @staticmethod
    def getQuestsType():
        return BaseQuestModel

    def _initialize(self):
        super(MetaViewModel, self)._initialize()
        self._addViewModelProperty('witchesWidget', WitchesModel())
        self._addBoolProperty('isViewHidden', False)
        self._addBoolProperty('isNew', False)
        self._addStringProperty('abilityIconName', '')
        self._addArrayProperty('quests', Array())
        self.onInfoClick = self._addCommand('onInfoClick')
        self.onAboutClick = self._addCommand('onAboutClick')
        self.onPreviewClick = self._addCommand('onPreviewClick')
        self.onShopClick = self._addCommand('onShopClick')
        self.onPhaseChange = self._addCommand('onPhaseChange')
