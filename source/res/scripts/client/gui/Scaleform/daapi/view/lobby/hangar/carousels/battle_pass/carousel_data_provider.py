# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/carousels/battle_pass/carousel_data_provider.py
from gui.battle_pass.battle_pass_constants import SUPPORTED_ARENA_BONUS_TYPES
from gui.battle_pass.battle_pass_helpers import getSupportedCurrentArenaBonusType
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
        gameMode = getSupportedCurrentArenaBonusType()
        if self._isBattlePassHidden(vehicle) or gameMode not in SUPPORTED_ARENA_BONUS_TYPES:
            return result
        currentPoints, limitPoints = self.battlePassController.getVehicleProgression(vehicle.intCD)
        isSpecialVehicle = self.battlePassController.isSpecialVehicle(vehicle.intCD)
        hasProgression = vehicle.level >= self.battlePassController.getMinVehLevelToEarnPoints()
        result['hasProgression'] = hasProgression
        if hasProgression:
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
