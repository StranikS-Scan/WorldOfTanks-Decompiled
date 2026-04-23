# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/customization/customization_types_model.py
from frameworks.wulf import ViewModel

class CustomizationTypesModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=13, commands=0):
        super(CustomizationTypesModel, self).__init__(properties=properties, commands=commands)

    def getPaint(self):
        return self._getNumber(0)

    def setPaint(self, value):
        self._setNumber(0, value)

    def getCamouflage(self):
        return self._getNumber(1)

    def setCamouflage(self, value):
        self._setNumber(1, value)

    def getModification(self):
        return self._getNumber(2)

    def setModification(self, value):
        self._setNumber(2, value)

    def getOutfit(self):
        return self._getNumber(3)

    def setOutfit(self, value):
        self._setNumber(3, value)

    def getStyle(self):
        return self._getNumber(4)

    def setStyle(self, value):
        self._setNumber(4, value)

    def getDecal(self):
        return self._getNumber(5)

    def setDecal(self, value):
        self._setNumber(5, value)

    def getEmblem(self):
        return self._getNumber(6)

    def setEmblem(self, value):
        self._setNumber(6, value)

    def getInscription(self):
        return self._getNumber(7)

    def setInscription(self, value):
        self._setNumber(7, value)

    def getProjectionDecal(self):
        return self._getNumber(8)

    def setProjectionDecal(self, value):
        self._setNumber(8, value)

    def getInsignia(self):
        return self._getNumber(9)

    def setInsignia(self, value):
        self._setNumber(9, value)

    def getPersonalNumber(self):
        return self._getNumber(10)

    def setPersonalNumber(self, value):
        self._setNumber(10, value)

    def getSequence(self):
        return self._getNumber(11)

    def setSequence(self, value):
        self._setNumber(11, value)

    def getAttachment(self):
        return self._getNumber(12)

    def setAttachment(self, value):
        self._setNumber(12, value)

    def _initialize(self):
        super(CustomizationTypesModel, self)._initialize()
        self._addNumberProperty('Paint', 0)
        self._addNumberProperty('Camouflage', 0)
        self._addNumberProperty('Modification', 0)
        self._addNumberProperty('Outfit', 0)
        self._addNumberProperty('Style', 0)
        self._addNumberProperty('Decal', 0)
        self._addNumberProperty('Emblem', 0)
        self._addNumberProperty('Inscription', 0)
        self._addNumberProperty('ProjectionDecal', 0)
        self._addNumberProperty('Insignia', 0)
        self._addNumberProperty('PersonalNumber', 0)
        self._addNumberProperty('Sequence', 0)
        self._addNumberProperty('Attachment', 0)
