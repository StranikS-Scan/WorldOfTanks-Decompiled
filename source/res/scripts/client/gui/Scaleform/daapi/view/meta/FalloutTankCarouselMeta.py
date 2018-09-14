# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FalloutTankCarouselMeta.py
from gui.Scaleform.daapi.view.lobby.hangar.carousels.basic.tank_carousel import TankCarousel

class FalloutTankCarouselMeta(TankCarousel):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends TankCarousel
    null
    """

    def changeVehicle(self, id):
        """
        :param id:
        :return :
        """
        self._printOverrideError('changeVehicle')

    def clearSlot(self, vehicleId):
        """
        :param vehicleId:
        :return :
        """
        self._printOverrideError('clearSlot')

    def shiftSlot(self, vehicleId):
        """
        :param vehicleId:
        :return :
        """
        self._printOverrideError('shiftSlot')

    def as_setMultiselectionInfoS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setMultiselectionInfo(data) if self._isDAAPIInited() else None

    def as_getMultiselectionDPS(self):
        """
        :return Object:
        """
        return self.flashObject.as_getMultiselectionDP() if self._isDAAPIInited() else None
