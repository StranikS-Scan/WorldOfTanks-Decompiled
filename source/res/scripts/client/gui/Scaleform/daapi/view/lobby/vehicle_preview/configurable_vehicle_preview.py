# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_preview/configurable_vehicle_preview.py
from gui.Scaleform.daapi.view.lobby.vehicle_preview.hangar_switchers import getHangarSwitcher, getHangarSoundSpace
from gui.Scaleform.daapi.view.lobby.vehicle_preview.vehicle_preview import VehiclePreview
from shared_utils import CONST_CONTAINER

class OptionalBlocks(CONST_CONTAINER):
    BUYING_PANEL = 'buyingPanel'
    CLOSE_BUTTON = 'closeBtn'
    ALL = (BUYING_PANEL, CLOSE_BUTTON)


class ConfigurableVehiclePreview(VehiclePreview):

    def __init__(self, ctx):
        hangarAlias = ctx.get('customHangarAlias')
        self.__hangarSwitcher = getHangarSwitcher(hangarAlias)
        soundSpace = getHangarSoundSpace(hangarAlias)
        if soundSpace is not None:
            self._COMMON_SOUND_SPACE = soundSpace
        super(ConfigurableVehiclePreview, self).__init__(ctx)
        self.__hiddenBlocks = ctx.get('hiddenBlocks')
        self.__showCloseBtn = OptionalBlocks.CLOSE_BUTTON not in self.__hiddenBlocks
        return

    def setBottomPanel(self):
        if OptionalBlocks.BUYING_PANEL in self.__hiddenBlocks:
            self.as_setBottomPanelS('')
        else:
            super(ConfigurableVehiclePreview, self).setBottomPanel()

    def _populate(self):
        super(ConfigurableVehiclePreview, self)._populate()
        if self.__hangarSwitcher:
            self.__hangarSwitcher.switchToHangar()

    def _dispose(self):
        super(ConfigurableVehiclePreview, self)._dispose()
        if self.__hangarSwitcher:
            self.__hangarSwitcher.returnFromHangar()
            self.__hangarSwitcher = None
        return

    def _getData(self):
        result = super(ConfigurableVehiclePreview, self)._getData()
        result.update({'showCloseBtn': self.__showCloseBtn})
        return result
