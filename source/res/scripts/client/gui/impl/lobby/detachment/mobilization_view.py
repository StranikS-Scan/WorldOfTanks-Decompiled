# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/mobilization_view.py
import typing
from Event import Event
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.auxiliary.detachment_helper import fillDetachmentWithPointsModel, fillDog
from gui.impl.auxiliary.instructors_helper import GUI_NO_INSTRUCTOR_ID
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.common.instructor_shown_page_constants import InstructorShownPageConstants
from gui.impl.gen.view_models.views.lobby.detachment.mobilization_view_model import MobilizationViewModel
from gui.impl.gen.view_models.views.lobby.detachment.tooltips.convertation_vehicle_tooltip_model import ConvertationVehicleTooltipModel
from gui.impl.lobby.detachment.navigation_view_impl import NavigationViewImpl
from gui.impl.lobby.detachment.tooltips.colored_simple_tooltip import ColoredSimpleTooltip
from gui.impl.lobby.detachment.tooltips.convertation_vehicle_tooltip_view import ConvertationVehicleTooltipView
from gui.impl.lobby.detachment.tooltips.detachment_info_tooltip import PreviewDetachmentInfoTooltip
from gui.impl.lobby.detachment.tooltips.instructor_tooltip import InstructorTooltip, EmptyInstructorTooltip
from gui.impl.lobby.detachment.tooltips.level_badge_tooltip_view import LevelBadgeTooltipView
from gui.impl.lobby.detachment.tooltips.points_info_tooltip_view import PointInfoTooltipView
from gui.shared.event_dispatcher import showConvertInfoWindow
from helpers import dependency
from items.components.detachment_constants import NO_DETACHMENT_ID
from nations import NAMES
from skeletons.gui.detachment import IDetachmentCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.gui_items import IGuiItemsFactory
from uilogging.detachment.constants import GROUP
from uilogging.detachment.loggers import DetachmentLogger, g_detachmentFlowLogger
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.detachment import Detachment

class MobilizationView(NavigationViewImpl):
    __slots__ = ('onContinue', 'onFlashLayoutUpdate', '_instructors', '_vehicle', '_detachment')
    _CLOSE_IN_PREBATTLE = True
    itemsFactory = dependency.descriptor(IGuiItemsFactory)
    itemsCache = dependency.descriptor(IItemsCache)
    detachmentCache = dependency.descriptor(IDetachmentCache)
    uiLogger = DetachmentLogger(GROUP.MOBILIZE_CREW)

    def __init__(self, ctx):
        settings = ViewSettings(R.views.lobby.detachment.MobilizationView())
        settings.flags = ViewFlags.COMPONENT
        settings.model = MobilizationViewModel()
        super(MobilizationView, self).__init__(settings, ctx=ctx)
        self.onFlashLayoutUpdate = Event()
        self.onContinue = Event()
        self._detachment = None
        self._vehicle = None
        self._instructors = []
        return

    def createToolTipContent(self, event, contentID):
        vehicle = self._vehicle
        detachment = self._detachment
        if contentID == R.views.lobby.detachment.tooltips.PointsInfoTooltip():
            PointInfoTooltipView.uiLogger.setGroup(self.uiLogger.group)
            return PointInfoTooltipView(event.contentID, detachmentDescr=detachment.getDescriptor())
        if contentID == R.views.lobby.detachment.tooltips.ColoredSimpleTooltip():
            return ColoredSimpleTooltip(event.getArgument('header', ''), event.getArgument('body', ''))
        if contentID == R.views.lobby.detachment.tooltips.InstructorTooltip():
            instrID = int(event.getArgument('instructorInvID'))
            if instrID == GUI_NO_INSTRUCTOR_ID and not self._instructors:
                return EmptyInstructorTooltip(detachment, True)
            if instrID != GUI_NO_INSTRUCTOR_ID and self._instructors:
                instructor = self._instructors[instrID]
                InstructorTooltip.uiLogger.setGroup(self.uiLogger.group)
                return InstructorTooltip(instructor, detachment, shownPage=InstructorShownPageConstants.COMMON)
        else:
            if contentID == R.views.lobby.detachment.tooltips.ConvertationVehicleTooltip():
                ConvertationVehicleTooltipView.uiLogger.setGroup(self.uiLogger.group)
                return ConvertationVehicleTooltipView(event.contentID, vehicle, state=ConvertationVehicleTooltipModel.MOBILIZATION)
            if contentID == R.views.lobby.detachment.tooltips.LevelBadgeTooltip():
                return LevelBadgeTooltipView(NO_DETACHMENT_ID, detachment)
            if contentID == R.views.lobby.detachment.tooltips.DetachmentInfoTooltip():
                return PreviewDetachmentInfoTooltip(detachment, self._instructors, vehicle)
        return super(MobilizationView, self).createToolTipContent(event, contentID)

    def _addListeners(self):
        super(MobilizationView, self)._addListeners()
        self.viewModel.onFlashLayoutUpdate += self._onFlashLayoutUpdate
        self.viewModel.onContinueClick += self._onContinueClick
        self.viewModel.onInfoClick += self._onInfoClick

    def _removeListeners(self):
        self.viewModel.onFlashLayoutUpdate -= self._onFlashLayoutUpdate
        self.viewModel.onContinueClick -= self._onContinueClick
        self.viewModel.onInfoClick -= self._onInfoClick
        super(MobilizationView, self)._removeListeners()

    def selectVehicle(self, vehicle):
        self._vehicle = vehicle
        with self.viewModel.transaction() as model:
            detachmentInfo = model.detachmentInfo
            fillDog(detachmentInfo, vehicle)
            detachmentInfo.setNation(NAMES[vehicle.nationID])

    def setDetachment(self, detDescr, instrDescrs, skinID):
        vehicle = self._vehicle
        if not vehicle:
            return
        self._detachment = self.itemsFactory.createDetachment(detDescr.makeCompactDescr(), skinID=skinID)
        with self.viewModel.transaction() as model:
            detachmentInfo = model.detachmentInfo
            self._instructors = fillDetachmentWithPointsModel(detachmentInfo, detDescr, skinID, instrDescrs, vehicle, itemsCache=self.itemsCache)

    def onEscapePress(self):
        self._onBack()

    def _finalize(self):
        self.onFlashLayoutUpdate.clear()
        self.onFlashLayoutUpdate = None
        super(MobilizationView, self)._finalize()
        return

    @property
    def viewModel(self):
        return super(MobilizationView, self).getViewModel()

    def _onFlashLayoutUpdate(self, args=None):
        self.onFlashLayoutUpdate(args)

    @g_detachmentFlowLogger.dFlow(uiLogger.group, GROUP.MOBILIZE_CREW_INFO)
    def _onInfoClick(self, args=None):
        showConvertInfoWindow()

    def _onContinueClick(self):
        self.onContinue()
