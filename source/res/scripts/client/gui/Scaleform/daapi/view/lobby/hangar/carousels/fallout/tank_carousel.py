# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/carousels/fallout/tank_carousel.py
from gui.game_control import getFalloutCtrl
from gui.prb_control.prb_helpers import GlobalListener
from gui.shared.formatters import text_styles
from gui.shared.formatters.ranges import toRomanRangeString
from gui.shared.utils.functions import makeTooltip
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.Scaleform import getButtonsAssetPath
from gui.Scaleform.daapi.view.lobby.hangar.carousels.fallout.carousel_data_provider import FalloutCarouselDataProvider
from gui.Scaleform.daapi.view.lobby.hangar.carousels.fallout.slot_data_provider import SlotDataProvider
from gui.Scaleform.daapi.view.lobby.hangar.carousels.fallout.carousel_filter import FalloutCarouselFilter
from gui.Scaleform.daapi.view.meta.FalloutTankCarouselMeta import FalloutTankCarouselMeta
from helpers import i18n, int2roman
_CAROUSEL_FILTERS = ('bonus', 'favorite', 'gameMode')

class FalloutTankCarousel(FalloutTankCarouselMeta, GlobalListener):

    def __init__(self):
        super(FalloutTankCarousel, self).__init__()
        self._usedFilters = _CAROUSEL_FILTERS
        self._carouselDPConfig.update({'falloutCtrl': None})
        self._carouselDPCls = FalloutCarouselDataProvider
        self._carouselFilterCls = FalloutCarouselFilter
        self._falloutCtrl = None
        return

    def changeVehicle(self, vehicleInvId):
        """ Add vehicle to fallout slot.
        
        :param vehicleInvId: vehicle's inventory id
        """
        if vehicleInvId in self._falloutCtrl.getSelectedSlots():
            self._falloutCtrl.removeSelectedVehicle(vehicleInvId)
        else:
            self._falloutCtrl.addSelectedVehicle(vehicleInvId)

    def clearSlot(self, vehicleInvId):
        """ Remove vehicle from fallout slot.
        
        :param vehicleInvId: vehicle's inventory id
        """
        self._falloutCtrl.removeSelectedVehicle(vehicleInvId)

    def shiftSlot(self, vehicleInvId):
        """ Shift vehicles in fallout slot clockwise.
        
        :param vehicleInvId: vehicle's inventory id
        """
        self._falloutCtrl.moveSelectedVehicle(vehicleInvId)

    def _populate(self):
        self._falloutCtrl = getFalloutCtrl()
        self._falloutCtrl.onVehiclesChanged += self._updateFalloutVehicles
        self._falloutCtrl.onSettingsChanged += self._updateFalloutSettings
        self._carouselDPConfig.update({'falloutCtrl': self._falloutCtrl})
        super(FalloutTankCarousel, self)._populate()
        self._slotDP = SlotDataProvider(self._falloutCtrl, self._itemsCache)
        self._slotDP.setFlashObject(self.as_getMultiselectionDPS())
        self._slotDP.buildList()
        self.as_setMultiselectionInfoS(self.__getMultiselectionInfoVO())

    def _dispose(self):
        self._falloutCtrl.onVehiclesChanged -= self._updateFalloutVehicles
        self._falloutCtrl.onSettingsChanged -= self._updateFalloutSettings
        self._falloutCtrl = None
        self._slotDP.fini()
        self._slotDP = None
        super(FalloutTankCarousel, self)._dispose()
        return

    def _updateFalloutSettings(self):
        if self._falloutCtrl is not None:
            self.updateVehicles()
            self.as_setMultiselectionInfoS(self.__getMultiselectionInfoVO())
            self._slotDP.buildList()
        return

    def _updateFalloutVehicles(self):
        self.updateVehicles(filterCriteria=REQ_CRITERIA.VEHICLE.FALLOUT.AVAILABLE)
        self.as_setMultiselectionInfoS(self.__getMultiselectionInfoVO())
        self._slotDP.buildList()

    def _getInitialFilterVO(self):
        data = super(FalloutTankCarousel, self)._getInitialFilterVO()
        filters = self.filter.getFilters(self._usedFilters)
        battleTypeStr = i18n.makeString('#menu:headerButtons/battle/menu/fallout/{}'.format(self._falloutCtrl.getBattleType()))
        data['hotFilters'].append({'value': getButtonsAssetPath('game_mode'),
         'selected': filters['gameMode'],
         'tooltip': makeTooltip('#tank_carousel_filter:filter/gameModeFilter/header', i18n.makeString('#tank_carousel_filter:filter/gameModeFilter/body', type=battleTypeStr))})
        return data

    def __getMultiselectionStatus(self):
        config = self._falloutCtrl.getConfig()
        battleType = self._falloutCtrl.getBattleType()
        messageTemplate = '#fallout:multiselectionSlot/{}'.format(battleType)
        if not config.hasRequiredVehicles():
            return (False, text_styles.critical(i18n.makeString('{}/topTierVehicleRequired'.format(messageTemplate), level=toRomanRangeString(config.allowedLevels, step=1), requiredLevel=int2roman(config.vehicleLevelRequired))))
        if self._falloutCtrl.getSelectedVehicles():
            return (True, text_styles.concatStylesToMultiLine(text_styles.middleTitle(i18n.makeString('#fallout:multiselectionSlot/selectionStatus')), text_styles.main(i18n.makeString('#fallout:multiselectionSlot/selectionRequirements', level=toRomanRangeString(config.allowedLevels, step=1)))))
        return (False, text_styles.concatStylesToMultiLine(text_styles.highTitle(i18n.makeString('{}/descriptionTitle'.format(messageTemplate), topLevel=int2roman(max(config.allowedLevels)))), text_styles.main(i18n.makeString('{}/message'.format(messageTemplate), level=toRomanRangeString(config.allowedLevels, step=1))))) if config.getAllowedVehicles() else (False, '')

    def __getMultiselectionInfoVO(self):
        allowedLevels = self._falloutCtrl.getConfig().allowedLevels
        showSlots, message = self.__getMultiselectionStatus()
        canDoAction, _ = self.prbDispatcher.canPlayerDoAction()
        if canDoAction:
            statusString = text_styles.statInfo('#fallout:multiselectionSlot/groupReady')
        else:
            statusString = text_styles.critical('#fallout:multiselectionSlot/groupNotReady')
        return {'formattedMessage': message,
         'showSlots': showSlots,
         'indicatorIsEnabled': canDoAction,
         'vehicleTypes': text_styles.concatStylesWithSpace(text_styles.middleTitle(i18n.makeString('#fallout:multiselectionSlot/selectionStatus')), text_styles.main(i18n.makeString('#fallout:multiselectionSlot/selectionRequirements', level=toRomanRangeString(allowedLevels, step=1)))),
         'statusSrt': statusString}
