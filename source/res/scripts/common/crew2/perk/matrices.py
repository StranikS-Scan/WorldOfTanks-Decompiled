# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/crew2/perk/matrices.py
import typing
import ResMgr
from crew2.perk.matrix import PerkMatrix
from items import _xml
from items.components.detachment_constants import DetachmentMaxValues

class PerkMatrices(object):
    __slots__ = '_matrices'

    def __init__(self, matricesPath):
        self._matrices = {}
        self.__load(matricesPath)

    def getMatrix(self, matrixID):
        return self._matrices.get(matrixID)

    def __load(self, path):
        section = ResMgr.openSection(path)
        if section is None:
            _xml.raiseWrongXml(None, path, 'can not open or read')
        xmlCtx = (None, path)
        self.__readPerkMatrices(xmlCtx, section)
        ResMgr.purge(path)
        return

    def __readPerkMatrices(self, xmlCtx, section):
        perkMatricesXmlCtx = (xmlCtx, 'perkMatrices')
        for _, perkMatrixSection in _xml.getChildren(xmlCtx, section, 'perkMatrices'):
            self.__readPerkMatrix(perkMatricesXmlCtx, perkMatrixSection)

    def __readPerkMatrix(self, xmlContext, perkMatrixSection):
        perkMatrixID = _xml.readInt(xmlContext, perkMatrixSection, 'id', 1, DetachmentMaxValues.PERKS_MATRIX_ID)
        perkMatrix = self._matrices.setdefault(perkMatrixID, PerkMatrix(perkMatrixID))
        perkMatrix.loadFromDataSection(xmlContext, perkMatrixSection)
