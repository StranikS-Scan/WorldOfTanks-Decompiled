# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/carousels/battle_pass/carousel_data_provider.py
from gui.Scaleform.daapi.view.lobby.hangar.carousels.basic.carousel_data_provider import HangarCarouselDataProvider
from gui.shared.formatters import text_styles
from helpers import dependency
from skeletons.gui.game_control import IBattlePassController

class BattlePassCarouselDataProvider(HangarCarouselDataProvider):
    battlePassController = dependency.descriptor(IBattlePassController)

    def _buildVehicle(self, vehicle):

        def formatSpecialVehPoints(value):
            return text_styles.makeHtmlString('html_templates:lobby/tank_carousel', 'specialVehPoints', ctx={'value': value})

        result = super(BattlePassCarouselDataProvider, self)._buildVehicle(vehicle)
        if self._isBattlePassHidden(vehicle):
            return result
        currentPoints, limitPoints = self.battlePassController.getVehicleProgression(vehicle.intCD)
        isSpecialVehicle = self.battlePassController.isSpecialVehicle(vehicle.intCD)
        result['hasProgression'] = limitPoints > 0
        if limitPoints > 0:
            limitReached = currentPoints >= limitPoints
            pointsFormatter = formatSpecialVehPoints if isSpecialVehicle and limitReached else text_styles.counterLabelText
            limitFormatter = formatSpecialVehPoints if isSpecialVehicle else text_styles.counterLabelText
            limitPointsFormatted = limitFormatter(' / {}'.format(limitPoints))
            result['progressionPoints'] = {'currentPoints': pointsFormatter(currentPoints),
             'limitPoints': limitPointsFormatted,
             'limitReached': limitReached,
             'isSpecialVehicle': isSpecialVehicle}
        return result

    def _isBattlePassHidden(self, vehicle):
        return not self._isSuitableForQueue(vehicle) or not self.battlePassController.isVisible()
