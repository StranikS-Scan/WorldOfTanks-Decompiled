# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/SkillDropMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class SkillDropMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    null
    """

    def calcDropSkillsParams(self, tmanCompDescr, xpReuseFraction):
        """
        :param tmanCompDescr:
        :param xpReuseFraction:
        :return Array:
        """
        self._printOverrideError('calcDropSkillsParams')

    def dropSkills(self, dropSkillCostIdx):
        """
        :param dropSkillCostIdx:
        :return :
        """
        self._printOverrideError('dropSkills')

    def as_setDataS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_setGoldS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_setGold(value) if self._isDAAPIInited() else None

    def as_setCreditsS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_setCredits(value) if self._isDAAPIInited() else None
