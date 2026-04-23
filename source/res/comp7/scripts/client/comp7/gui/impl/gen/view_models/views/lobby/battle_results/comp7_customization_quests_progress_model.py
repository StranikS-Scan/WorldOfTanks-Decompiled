# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/gen/view_models/views/lobby/battle_results/comp7_customization_quests_progress_model.py
from frameworks.wulf import Array, ViewModel
from comp7.gui.impl.gen.view_models.views.lobby.battle_results.comp7_customization_quest_progress_model import Comp7CustomizationQuestProgressModel

class Comp7CustomizationQuestsProgressModel(ViewModel):
    __slots__ = ()
    PATH = 'coui://comp7/gui/gameface/_dist/production/mono/plugins/lobby/customization_quests/customization_quests.js'

    def __init__(self, properties=1, commands=0):
        super(Comp7CustomizationQuestsProgressModel, self).__init__(properties=properties, commands=commands)

    def getCustomizationQuests(self):
        return self._getArray(0)

    def setCustomizationQuests(self, value):
        self._setArray(0, value)

    @staticmethod
    def getCustomizationQuestsType():
        return Comp7CustomizationQuestProgressModel

    def _initialize(self):
        super(Comp7CustomizationQuestsProgressModel, self)._initialize()
        self._addArrayProperty('customizationQuests', Array())
