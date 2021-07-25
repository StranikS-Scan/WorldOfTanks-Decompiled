# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/tooltips/perk_tooltip_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.common.perk_short_model import PerkShortModel
from gui.impl.gen.view_models.views.lobby.detachment.tooltips.perk_bonus_model import PerkBonusModel
from gui.impl.gen.view_models.views.lobby.detachment.tooltips.perk_progress_model import PerkProgressModel
from gui.impl.gen.view_models.views.lobby.detachment.tooltips.perk_veh_param_model import PerkVehParamModel

class PerkTooltipModel(PerkShortModel):
    __slots__ = ()
    MATRIX_PERK_TOOLTIP = 'MATRIX_PERK_TOOLTIP'
    DETACHMENT_PERK_TOOLTIP = 'DETACHMENT_PERK_TOOLTIP'
    DETACHMENT_PERK_TOOLTIP_SHORT = 'DETACHMENT_PERK_TOOLTIP_SHORT'
    INSTRUCTOR_PERK_TOOLTIP = 'INSTRUCTOR_PERK_TOOLTIP'
    TTC_PERK_TOOLTIP = 'TTC_PERK_TOOLTIP'

    def __init__(self, properties=23, commands=0):
        super(PerkTooltipModel, self).__init__(properties=properties, commands=commands)

    @property
    def progress(self):
        return self._getViewModel(9)

    @property
    def progressMax(self):
        return self._getViewModel(10)

    def getIconName(self):
        return self._getString(11)

    def setIconName(self, value):
        self._setString(11, value)

    def getBranchName(self):
        return self._getResource(12)

    def setBranchName(self, value):
        self._setResource(12, value)

    def getBranchIconName(self):
        return self._getString(13)

    def setBranchIconName(self, value):
        self._setString(13, value)

    def getMovie(self):
        return self._getString(14)

    def setMovie(self, value):
        self._setString(14, value)

    def getTempPoints(self):
        return self._getNumber(15)

    def setTempPoints(self, value):
        self._setNumber(15, value)

    def getIsUltimate(self):
        return self._getBool(16)

    def setIsUltimate(self, value):
        self._setBool(16, value)

    def getIsPermanent(self):
        return self._getBool(17)

    def setIsPermanent(self, value):
        self._setBool(17, value)

    def getType(self):
        return self._getString(18)

    def setType(self, value):
        self._setString(18, value)

    def getDescription(self):
        return self._getString(19)

    def setDescription(self, value):
        self._setString(19, value)

    def getInstructorsBonuses(self):
        return self._getArray(20)

    def setInstructorsBonuses(self, value):
        self._setArray(20, value)

    def getBoostersBonuses(self):
        return self._getArray(21)

    def setBoostersBonuses(self, value):
        self._setArray(21, value)

    def getVehParams(self):
        return self._getArray(22)

    def setVehParams(self, value):
        self._setArray(22, value)

    def _initialize(self):
        super(PerkTooltipModel, self)._initialize()
        self._addViewModelProperty('progress', PerkProgressModel())
        self._addViewModelProperty('progressMax', PerkProgressModel())
        self._addStringProperty('iconName', '')
        self._addResourceProperty('branchName', R.invalid())
        self._addStringProperty('branchIconName', '')
        self._addStringProperty('movie', '')
        self._addNumberProperty('tempPoints', 0)
        self._addBoolProperty('isUltimate', False)
        self._addBoolProperty('isPermanent', False)
        self._addStringProperty('type', '')
        self._addStringProperty('description', '')
        self._addArrayProperty('instructorsBonuses', Array())
        self._addArrayProperty('boostersBonuses', Array())
        self._addArrayProperty('vehParams', Array())
