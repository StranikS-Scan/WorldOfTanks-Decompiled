# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_compare/cmp_configurator_base.py
import typing
from gui.Scaleform.daapi.view.meta.VehicleCompareConfiguratorBaseViewMeta import VehicleCompareConfiguratorBaseViewMeta
if typing.TYPE_CHECKING:
    from typing import Optional
    from gui.Scaleform.daapi.view.lobby.vehicle_compare.cmp_configurator_view import VehicleCompareConfiguratorMain

class VehicleCompareConfiguratorBaseView(VehicleCompareConfiguratorBaseViewMeta):

    def __init__(self):
        super(VehicleCompareConfiguratorBaseView, self).__init__()
        self._container = None
        self.__isInited = False
        return

    def onShow(self):
        pass

    def onCamouflageUpdated(self):
        pass

    def onShellsUpdated(self, updateShells=False, selectedIndex=-1):
        pass

    def onOptDeviceUpdated(self):
        pass

    def onEquipmentUpdated(self):
        pass

    def onModulesUpdated(self):
        pass

    def onPerksUpdated(self):
        pass

    def onResetToDefault(self):
        pass

    def setContainer(self, container):
        self._container = container
        self.__tryToInit()

    def _init(self):
        pass

    def _populate(self):
        super(VehicleCompareConfiguratorBaseView, self)._populate()
        self.__tryToInit()

    def _dispose(self):
        self._container = None
        super(VehicleCompareConfiguratorBaseView, self)._dispose()
        return

    def __tryToInit(self):
        if self.isCreated() and self._container is not None and not self.__isInited:
            self.__isInited = True
            self._init()
        return
