# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/dialogs/vehicle_hint_dialog_builder.py
import typing
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl import backport
from gui.impl.dialogs.dialog_template_button import CancelButton
from gui.impl.dialogs.gf_builders import BaseDialogBuilder
from gui.impl.dialogs.sub_views.title.simple_text_title import SimpleTextTitle
from gui.impl.gen import R
from gui.impl.gen.view_models.views.dialogs.default_dialog_place_holders import DefaultDialogPlaceHolders
from gui.impl.gen.view_models.views.dialogs.dialog_template_button_view_model import ButtonType
from gui.impl.gen.view_models.views.lobby.new_year.dialogs.levels_range_model import LevelsRangeModel
from gui.impl.new_year.new_year_helper import formatRomanNumber
from gui.impl.pub import ViewImpl
from gui.impl.pub.dialog_window import DialogButtons
from helpers import dependency
from new_year.vehicle_branch_helpers import getAvailableVehicleLevels
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController
if typing.TYPE_CHECKING:
    from gui.impl.dialogs.dialog_template import DialogTemplateView

class LevelsRange(ViewImpl):
    __slots__ = ()
    __nyController = dependency.descriptor(INewYearController)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.new_year.dialogs.LevelsRange())
        settings.flags = ViewFlags.COMPONENT
        settings.model = LevelsRangeModel()
        super(LevelsRange, self).__init__(settings)

    @property
    def viewModel(self):
        return super(LevelsRange, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(LevelsRange, self)._initialize()
        with self.viewModel.transaction() as model:
            minLevel, maxLevel = getAvailableVehicleLevels()
            model.setStartLevel(minLevel)
            model.setCurrentLevel(maxLevel)


class VehicleHintDialogBuilder(BaseDialogBuilder):
    __itemsCache = dependency.descriptor(IItemsCache)

    def _extendTemplate(self, template):
        super(VehicleHintDialogBuilder, self)._extendTemplate(template)
        levelNum = self.__itemsCache.items.festivity.getMaxLevel()
        title = backport.text(R.strings.ny.dialogs.vehicleHint.title(), level=formatRomanNumber(levelNum))
        template.setSubView(DefaultDialogPlaceHolders.TITLE, SimpleTextTitle(title))
        template.setSubView(DefaultDialogPlaceHolders.CONTENT, LevelsRange())
        template.addButton(CancelButton(R.strings.ny.dialogs.vehicleHint.submit(), DialogButtons.CANCEL, ButtonType.PRIMARY))
