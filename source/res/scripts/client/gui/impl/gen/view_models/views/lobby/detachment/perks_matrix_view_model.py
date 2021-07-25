# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/perks_matrix_view_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.detachment.common.detachment_right_panel_model import DetachmentRightPanelModel
from gui.impl.gen.view_models.views.lobby.detachment.common.detachment_short_info_model import DetachmentShortInfoModel
from gui.impl.gen.view_models.views.lobby.detachment.common.navigation_view_model import NavigationViewModel
from gui.impl.gen.view_models.views.lobby.detachment.common.price_model import PriceModel
from gui.impl.gen.view_models.views.lobby.detachment.perks_matrix.branch_model import BranchModel

class PerksMatrixViewModel(NavigationViewModel):
    __slots__ = ('onAddPointToPerk', 'onAddMaxPointsToPerk', 'onRemovePointFromPerk', 'onRemoveUnsavedPointsFromPerk', 'onRemoveAllPointsFromPerk', 'onSelectUltimatePerk', 'onUnselectUltimatePerk', 'onTogglePerksHighlighting', 'onSaveChangesClick', 'onCancelChangesClick', 'onClearMatrixClick', 'onGoToEditModeClick', 'onHighlightInstructorsByPerk', 'onHighlightPerksByInstructor', 'onHighlightRoseByBranch', 'onHighlightBranchByRose', 'onHidePerkTooltip')

    def __init__(self, properties=16, commands=20):
        super(PerksMatrixViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def detachmentInfo(self):
        return self._getViewModel(2)

    @property
    def editPriceInCurrency(self):
        return self._getViewModel(3)

    @property
    def rightPanelModel(self):
        return self._getViewModel(4)

    def getBranchesList(self):
        return self._getArray(5)

    def setBranchesList(self, value):
        self._setArray(5, value)

    def getAvailablePoints(self):
        return self._getNumber(6)

    def setAvailablePoints(self, value):
        self._setNumber(6, value)

    def getUnsavedSetPoints(self):
        return self._getNumber(7)

    def setUnsavedSetPoints(self, value):
        self._setNumber(7, value)

    def getHasUnsavedSelectedUltimatePerk(self):
        return self._getBool(8)

    def setHasUnsavedSelectedUltimatePerk(self, value):
        self._setBool(8, value)

    def getHasUnsavedEditPoints(self):
        return self._getBool(9)

    def setHasUnsavedEditPoints(self, value):
        self._setBool(9, value)

    def getHasSavedPoints(self):
        return self._getBool(10)

    def setHasSavedPoints(self, value):
        self._setBool(10, value)

    def getIsEditModeEnabled(self):
        return self._getBool(11)

    def setIsEditModeEnabled(self, value):
        self._setBool(11, value)

    def getIsOperationChargeable(self):
        return self._getBool(12)

    def setIsOperationChargeable(self, value):
        self._setBool(12, value)

    def getArePerksHighlighted(self):
        return self._getBool(13)

    def setArePerksHighlighted(self, value):
        self._setBool(13, value)

    def getEditPriceInBlanks(self):
        return self._getNumber(14)

    def setEditPriceInBlanks(self, value):
        self._setNumber(14, value)

    def getIsPerksHighlightingDisabled(self):
        return self._getBool(15)

    def setIsPerksHighlightingDisabled(self, value):
        self._setBool(15, value)

    def _initialize(self):
        super(PerksMatrixViewModel, self)._initialize()
        self._addViewModelProperty('detachmentInfo', DetachmentShortInfoModel())
        self._addViewModelProperty('editPriceInCurrency', PriceModel())
        self._addViewModelProperty('rightPanelModel', DetachmentRightPanelModel())
        self._addArrayProperty('branchesList', Array())
        self._addNumberProperty('availablePoints', 0)
        self._addNumberProperty('unsavedSetPoints', 0)
        self._addBoolProperty('hasUnsavedSelectedUltimatePerk', False)
        self._addBoolProperty('hasUnsavedEditPoints', False)
        self._addBoolProperty('hasSavedPoints', False)
        self._addBoolProperty('isEditModeEnabled', False)
        self._addBoolProperty('isOperationChargeable', False)
        self._addBoolProperty('arePerksHighlighted', False)
        self._addNumberProperty('editPriceInBlanks', 0)
        self._addBoolProperty('isPerksHighlightingDisabled', False)
        self.onAddPointToPerk = self._addCommand('onAddPointToPerk')
        self.onAddMaxPointsToPerk = self._addCommand('onAddMaxPointsToPerk')
        self.onRemovePointFromPerk = self._addCommand('onRemovePointFromPerk')
        self.onRemoveUnsavedPointsFromPerk = self._addCommand('onRemoveUnsavedPointsFromPerk')
        self.onRemoveAllPointsFromPerk = self._addCommand('onRemoveAllPointsFromPerk')
        self.onSelectUltimatePerk = self._addCommand('onSelectUltimatePerk')
        self.onUnselectUltimatePerk = self._addCommand('onUnselectUltimatePerk')
        self.onTogglePerksHighlighting = self._addCommand('onTogglePerksHighlighting')
        self.onSaveChangesClick = self._addCommand('onSaveChangesClick')
        self.onCancelChangesClick = self._addCommand('onCancelChangesClick')
        self.onClearMatrixClick = self._addCommand('onClearMatrixClick')
        self.onGoToEditModeClick = self._addCommand('onGoToEditModeClick')
        self.onHighlightInstructorsByPerk = self._addCommand('onHighlightInstructorsByPerk')
        self.onHighlightPerksByInstructor = self._addCommand('onHighlightPerksByInstructor')
        self.onHighlightRoseByBranch = self._addCommand('onHighlightRoseByBranch')
        self.onHighlightBranchByRose = self._addCommand('onHighlightBranchByRose')
        self.onHidePerkTooltip = self._addCommand('onHidePerkTooltip')
