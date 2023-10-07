# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/hangar_crew_widget.py
from CurrentVehicle import g_currentVehicle
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.hangar_crew_widget_model import HangarCrewWidgetModel
from gui.impl.lobby.crew.widget.crew_widget import CrewWidget
from gui.impl.pub import ViewImpl
from gui.shared.event_dispatcher import showPersonalCase, showChangeCrewMember
from gui.shared.gui_items.Tankman import NO_TANKMAN
from gui.shared.gui_items.Vehicle import NO_VEHICLE_ID
from helpers import dependency
from skeletons.gui.shared import IItemsCache

class HangarCrewWidget(ViewImpl):
    __slots__ = ('crewWidget',)
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        layoutID = R.views.lobby.crew.HangarCrewWidget()
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = HangarCrewWidgetModel()
        self.crewWidget = CrewWidget(vehicleInvID=g_currentVehicle.invID if g_currentVehicle.isPresent() else NO_VEHICLE_ID, currentViewID=layoutID)
        super(HangarCrewWidget, self).__init__(settings)

    @property
    def viewModel(self):
        return super(HangarCrewWidget, self).getViewModel()

    def updateTankmen(self, diff=None):
        _ = self.itemsCache.items.getTankmen()
        self.viewModel.setSyncInitiator(self.viewModel.getSyncInitiator() + 1)
        self.crewWidget.updateVehicleInvID(g_currentVehicle.invID)
        self.crewWidget.updateDisableState(g_currentVehicle.isInBattle() or g_currentVehicle.isInPrebattle() if g_currentVehicle.isPresent() else True)

    def _onLoading(self, *args, **kwargs):
        super(HangarCrewWidget, self)._onLoading(*args, **kwargs)
        self.setChildView(CrewWidget.LAYOUT_DYN_ACCESSOR(), self.crewWidget)

    def _getEvents(self):
        return ((self.crewWidget.onSlotClick, self.__onWidgetSlotClick),)

    def __onWidgetSlotClick(self, tankmanID, slotIdx):
        if tankmanID == NO_TANKMAN:
            showChangeCrewMember(slotIdx, g_currentVehicle.invID, self.layoutID)
        else:
            showPersonalCase(int(tankmanID), previousViewID=self.layoutID)
