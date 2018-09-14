# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/carousels/fallout/tank_carousel.py
from gui.Scaleform.daapi.view.lobby.hangar.carousels.basic.tank_carousel import FilterSetupContext
from gui.Scaleform.daapi.view.lobby.hangar.carousels.fallout.carousel_data_provider import FalloutCarouselDataProvider
from gui.Scaleform.daapi.view.lobby.hangar.carousels.fallout.carousel_filter import FalloutCarouselFilter
from gui.Scaleform.daapi.view.lobby.hangar.carousels.fallout.slot_data_provider import SlotDataProvider
from gui.Scaleform.daapi.view.meta.FalloutTankCarouselMeta import FalloutTankCarouselMeta
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared.formatters import text_styles
from gui.shared.formatters.ranges import toRomanRangeString
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import i18n, int2roman, dependency
from skeletons.gui.game_control import IFalloutController
_CAROUSEL_FILTERS = ('bonus', 'favorite', 'gameMode')

class FalloutTankCarousel(FalloutTankCarouselMeta, IGlobalListener):
    falloutCtrl = dependency.descriptor(IFalloutController)

    def __init__(self):
        super(FalloutTankCarousel, self).__init__()
        self._usedFilters = _CAROUSEL_FILTERS
        self._carouselDPConfig.update({'falloutCtrl': None})
        self._carouselDPCls = FalloutCarouselDataProvider
        self._carouselFilterCls = FalloutCarouselFilter
        self._slotDP = None
        return

    def changeVehicle(self, vehicleInvId):
        """ Add vehicle to fallout slot.
        
        :param vehicleInvId: vehicle's inventory id
        """
        if vehicleInvId in self.falloutCtrl.getSelectedSlots():
            self.falloutCtrl.removeSelectedVehicle(vehicleInvId)
        else:
            self.falloutCtrl.addSelectedVehicle(vehicleInvId)

    def clearSlot(self, vehicleInvId):
        """ Remove vehicle from fallout slot.
        
        :param vehicleInvId: vehicle's inventory id
        """
        self.falloutCtrl.removeSelectedVehicle(vehicleInvId)

    def shiftSlot(self, vehicleInvId):
        """ Shift vehicles in fallout slot clockwise.
        
        :param vehicleInvId: vehicle's inventory id
        """
        self._falloutCtrl.moveSelectedVehicle(vehicleInvId)

    def _populate(self):
        self.falloutCtrl.onVehiclesChanged += self._updateFalloutVehicles
        self.falloutCtrl.onSettingsChanged += self._updateFalloutSettings
        self._carouselDPConfig.update({'falloutCtrl': self.falloutCtrl})
        super(FalloutTankCarousel, self)._populate()
        self._slotDP = SlotDataProvider(self.falloutCtrl, self._itemsCache)
        self._slotDP.setFlashObject(self.as_getMultiselectionDPS())
        self._slotDP.buildList()
        self.as_setMultiselectionInfoS(self.__getMultiselectionInfoVO())

    def _dispose(self):
        self.falloutCtrl.onVehiclesChanged -= self._updateFalloutVehicles
        self.falloutCtrl.onSettingsChanged -= self._updateFalloutSettings
        self._slotDP.fini()
        self._slotDP = None
        super(FalloutTankCarousel, self)._dispose()
        return

    def _updateFalloutSettings(self):
        if self.falloutCtrl is not None:
            self.updateVehicles()
            self.as_setMultiselectionInfoS(self.__getMultiselectionInfoVO())
            self._slotDP.buildList()
        return

    def _updateFalloutVehicles(self):
        self.updateVehicles(filterCriteria=REQ_CRITERIA.VEHICLE.FALLOUT.AVAILABLE)
        self.as_setMultiselectionInfoS(self.__getMultiselectionInfoVO())
        self._slotDP.buildList()

    def _getFilterSetupContexts(self):
        contexts = super(FalloutTankCarousel, self)._getFilterSetupContexts()
        battleType = i18n.makeString('#menu:headerButtons/battle/menu/fallout/{}'.format(self.falloutCtrl.getBattleType()))
        contexts['gameMode'] = FilterSetupContext(ctx={'battleType': battleType})
        return contexts

    def __getMultiselectionStatus(self):
        config = self.falloutCtrl.getConfig()
        battleType = self.falloutCtrl.getBattleType()
        messageTemplate = '#fallout:multiselectionSlot/{}'.format(battleType)
        if not config.hasRequiredVehicles():
            return (False, text_styles.critical(i18n.makeString('{}/topTierVehicleRequired'.format(messageTemplate), level=toRomanRangeString(config.allowedLevels, step=1), requiredLevel=int2roman(config.vehicleLevelRequired))))
        if self.falloutCtrl.getSelectedVehicles():
            return (True, text_styles.concatStylesToMultiLine(text_styles.middleTitle(i18n.makeString('#fallout:multiselectionSlot/selectionStatus')), text_styles.main(i18n.makeString('#fallout:multiselectionSlot/selectionRequirements', level=toRomanRangeString(config.allowedLevels, step=1)))))
        return (False, text_styles.concatStylesToMultiLine(text_styles.highTitle(i18n.makeString('{}/descriptionTitle'.format(messageTemplate), topLevel=int2roman(max(config.allowedLevels)))), text_styles.main(i18n.makeString('{}/message'.format(messageTemplate), level=toRomanRangeString(config.allowedLevels, step=1))))) if config.getAllowedVehicles() else (False, '')

    def __getMultiselectionInfoVO(self):
        allowedLevels = self.falloutCtrl.getConfig().allowedLevels
        showSlots, message = self.__getMultiselectionStatus()
        result = self.prbEntity.canPlayerDoAction()
        if result.isValid:
            statusString = text_styles.statInfo('#fallout:multiselectionSlot/groupReady')
        else:
            statusString = text_styles.critical('#fallout:multiselectionSlot/groupNotReady')
        return {'formattedMessage': message,
         'showSlots': showSlots,
         'indicatorIsEnabled': result.isValid,
         'vehicleTypes': text_styles.concatStylesWithSpace(text_styles.middleTitle(i18n.makeString('#fallout:multiselectionSlot/selectionStatus')), text_styles.main(i18n.makeString('#fallout:multiselectionSlot/selectionRequirements', level=toRomanRangeString(allowedLevels, step=1)))),
         'statusSrt': statusString}
