# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/messengerBar/VehicleCompareCartButton.py
from gui.Scaleform.daapi.view.meta.ButtonWithCounterMeta import ButtonWithCounterMeta
from helpers import dependency
from skeletons.gui.game_control import IVehicleComparisonBasket

class VehicleCompareCartButton(ButtonWithCounterMeta):
    comparisonBasket = dependency.descriptor(IVehicleComparisonBasket)

    def _populate(self):
        super(VehicleCompareCartButton, self)._populate()
        self.comparisonBasket.onChange += self.__onCountChanged
        self.comparisonBasket.onSwitchChange += self.__onVehCmpBasketStateChanged
        self.__changeCount(self.comparisonBasket.getVehiclesCount())

    def _dispose(self):
        self.comparisonBasket.onChange -= self.__onCountChanged
        self.comparisonBasket.onSwitchChange -= self.__onVehCmpBasketStateChanged
        super(VehicleCompareCartButton, self)._dispose()

    def __onVehCmpBasketStateChanged(self):
        if not self.comparisonBasket.isEnabled():
            self.destroy()

    def __onCountChanged(self, _):
        """
        gui.game_control.VehComparisonBasket.onChange event handler
        :param _: instance of gui.game_control.veh_comparison_basket._ChangedData
        """
        self.__changeCount(self.comparisonBasket.getVehiclesCount())

    def __changeCount(self, count):
        self.as_setCountS(count)
