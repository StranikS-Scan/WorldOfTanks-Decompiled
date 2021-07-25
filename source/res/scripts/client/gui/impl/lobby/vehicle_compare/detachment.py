# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/vehicle_compare/detachment.py
import random
import typing
from Event import Event
from crew2 import settings_globals
from frameworks.wulf import ViewSettings, ViewFlags
from gui.Scaleform.daapi.view.lobby.vehicle_compare import cmp_helpers
from gui.game_control.veh_comparison_basket import PerksData
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.common.perk_short_model import PerkShortModel
from gui.impl.gen.view_models.views.lobby.detachment.tooltips.spent_points_tooltip_model import SpentPointsTooltipModel
from gui.impl.gen.view_models.views.lobby.detachment.vehicle_compare_detachment_widget_model import VehicleCompareDetachmentWidgetModel
from gui.impl.pub import ViewImpl
if typing.TYPE_CHECKING:
    from typing import List
    from crew2.perk.settings import PerkSettings
_PERKS_IN_ROW = 9
_PERK_ROWS_TO_HEIGHT = [230,
 145,
 220,
 275]

def _getAllPerks(matrixID):
    perkSettings = settings_globals.g_perkSettings
    perkMatrix = perkSettings.matrices.getMatrix(matrixID)
    return [ perk.id for perk in perkMatrix.perks.itervalues() ]


def _createPerkVM(perkID, perkPoint, instructorPoints):
    perkVM = PerkShortModel()
    perkVM.setId(perkID)
    perkVM.setPoints(perkPoint)
    perkVM.setInstructorPoints(instructorPoints)
    perkVM.setIcon(backport.image(R.images.gui.maps.icons.perks.normal.c_48x48.dyn('perk_{}'.format(perkID))()))
    return perkVM


class CompareDetachmentView(ViewImpl):
    __slots__ = ('onSetHeight', 'height', 'perkList', '__allPerks', '__perks')

    def __init__(self):
        settings = ViewSettings(R.views.lobby.detachment.VehicleCompareDetachmentWidget())
        settings.flags = ViewFlags.COMPONENT
        settings.model = VehicleCompareDetachmentWidgetModel()
        self.height = 0
        self.perkList = list()
        self.onSetHeight = Event()
        self.__allPerks = _getAllPerks(1)
        self.__perks = PerksData()
        super(CompareDetachmentView, self).__init__(settings)
        self.__determineWidgetHeight()

    @property
    def viewModel(self):
        return super(CompareDetachmentView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.detachment.tooltips.SpentPointsTooltip():
            model = SpentPointsTooltipModel()
            model.setPoints(len(self.__perks.points.keys()))
            model.setInstructorPoints(len(self.__perks.instructorPoints.keys()))
            return ViewImpl(ViewSettings(contentID, model=model))
        return super(CompareDetachmentView, self).createToolTipContent(event, contentID)

    def setPerks(self, perks):
        if self.__perks != perks:
            self.__perks = perks
            self.__setPerks(perks)
            self.__determineWidgetHeight()

    def _onLoading(self, *args, **kwargs):
        self.viewModel.setIsInDevelopment(True)

    def _initialize(self, *args, **kwargs):
        super(CompareDetachmentView, self)._initialize(*args, **kwargs)
        self.viewModel.onEdit += self.__onEdit
        self.viewModel.onClear += self.__onClear

    def _finalize(self):
        self.viewModel.onEdit -= self.__onEdit
        self.viewModel.onClear -= self.__onClear
        super(CompareDetachmentView, self)._finalize()

    def __determineWidgetHeight(self):
        height = _PERK_ROWS_TO_HEIGHT[0]
        if self.height != height:
            self.height = height
            self.onSetHeight()

    def __setPerks(self, perks):
        with self.viewModel.transaction() as tx:
            perkList = tx.getPerkList()
            self.__allPerks.extend([ perk.getId() for perk in perkList ])
            perkList.clear()
            perkCount = 0
            for perkID, count in perks.points.iteritems():
                self.__allPerks.remove(perkID)
                perkList.addViewModel(_createPerkVM(perkID, count, 0))
                perkCount += count

            instructorPerkCount = 0
            for perkID, count in perks.instructorPoints.iteritems():
                self.__allPerks.remove(perkID)
                perkList.addViewModel(_createPerkVM(perkID, 0, count))
                instructorPerkCount += count

            tx.setPoints(perkCount)
            tx.setInstructorPoints(instructorPerkCount)

    def __onEdit(self):
        if self.__allPerks:
            cmpMainView = cmp_helpers.getCmpConfiguratorMainView()
            perks = self.__perks.clone()
            perkID = self.__allPerks[0]
            if random.random() > 0.5:
                perks.instructorPoints.update({perkID: 1})
            else:
                perks.points.update({perkID: 1})
            cmpMainView.setPerks(perks)

    def __onClear(self):
        cmpMainView = cmp_helpers.getCmpConfiguratorMainView()
        cmpMainView.setPerks(PerksData())
