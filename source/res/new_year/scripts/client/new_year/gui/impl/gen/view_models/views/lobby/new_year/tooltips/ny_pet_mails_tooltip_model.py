# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/tooltips/ny_pet_mails_tooltip_model.py
from frameworks.wulf import ViewModel

class NyPetMailsTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(NyPetMailsTooltipModel, self).__init__(properties=properties, commands=commands)

    def getMailsAmount(self):
        return self._getNumber(0)

    def setMailsAmount(self, value):
        self._setNumber(0, value)

    def getNextMailTime(self):
        return self._getNumber(1)

    def setNextMailTime(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(NyPetMailsTooltipModel, self)._initialize()
        self._addNumberProperty('mailsAmount', 0)
        self._addNumberProperty('nextMailTime', 0)
