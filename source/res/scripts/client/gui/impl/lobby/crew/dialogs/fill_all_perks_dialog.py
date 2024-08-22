# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/dialogs/fill_all_perks_dialog.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.dialogs.dialog_template_button import ConfirmButton, CancelButton
from gui.impl.gen.resources import R
from gui.impl.gen.view_models.views.lobby.crew.common.tooltip_constants import TooltipConstants
from gui.impl.gen.view_models.views.lobby.crew.dialogs.fill_all_perks_dialog_model import FillAllPerksDialogModel
from gui.impl.gen.view_models.views.lobby.crew.dialogs.fill_all_perks_dialog_row import FillAllPerksDialogRow
from gui.impl.lobby.crew.dialogs.recruit_window.base_crew_dialog_template_with_blur_view import BaseCrewDialogTemplateWithBlurView
from helpers import dependency
from items.components.skills_constants import ORDERED_ROLES
from items.tankmen_cfg import getAutoFillConfig
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.shared import IItemsCache
from uilogging.crew_nps.loggers import CrewNpsDialogLogger
from uilogging.crew_nps.logging_constants import CrewNpsDialogKeys, CrewNpsViewKeys

class FillAllPerksDialog(BaseCrewDialogTemplateWithBlurView):
    itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ('__appliedForBarracks', '__toolTipMgr')
    LAYOUT_ID = R.views.lobby.crew.dialogs.FillAllPerksDialog()
    VIEW_MODEL = FillAllPerksDialogModel
    __appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, **kwargs):
        kwargs.setdefault('parentViewKey', CrewNpsViewKeys.BARRACKS)
        kwargs.setdefault('loggingKey', CrewNpsDialogKeys.FILL_ALL_PERKS)
        kwargs.setdefault('loggerClass', CrewNpsDialogLogger)
        super(FillAllPerksDialog, self).__init__(**kwargs)
        self.__appliedForBarracks = False
        self.__toolTipMgr = self.__appLoader.getApp().getToolTipMgr()

    @property
    def viewModel(self):
        return self.getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            if tooltipId == TooltipConstants.SKILL:
                skillName = str(event.getArgument('skillName'))
                args = [skillName, None, None]
                self.__toolTipMgr.onCreateWulfTooltip(TOOLTIPS_CONSTANTS.CREW_PERK_GF, args, event.mouse.positionX, event.mouse.positionY, parent=self.getParentWindow())
                return TOOLTIPS_CONSTANTS.CREW_PERK_GF
        return super(FillAllPerksDialog, self).createToolTip(event)

    def _onLoading(self, *args, **kwargs):
        cfg = getAutoFillConfig()
        rows = self.viewModel.getRows()
        for role in ORDERED_ROLES:
            skills = cfg.get(role)
            row = FillAllPerksDialogRow()
            row.setRole(role)
            rowSkills = row.getSkills()
            for skill in skills:
                rowSkills.addString(skill)

            rows.addViewModel(row)

        hasAnyTmanInBarracks = self.itemsCache.items.hasAnyTmanInBarracks()
        self.viewModel.setAreBarracksEmpty(not hasAnyTmanInBarracks)
        self.addButton(ConfirmButton(R.strings.dialogs.fillAllPerks.button.fill()))
        self.addButton(CancelButton(R.strings.dialogs.fillAllPerks.button.cancel()))
        super(FillAllPerksDialog, self)._onLoading(*args, **kwargs)

    def _getEvents(self):
        baseEvents = super(FillAllPerksDialog, self)._getEvents()
        return baseEvents + ((self.viewModel.onChange, self._onChange),)

    def _getAdditionalData(self):
        return self.__appliedForBarracks

    def _onChange(self):
        self.__appliedForBarracks = not self.__appliedForBarracks
        with self.viewModel.transaction():
            self.viewModel.setAppliedForBarracks(self.__appliedForBarracks)
