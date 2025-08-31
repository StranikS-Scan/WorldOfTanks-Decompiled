# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/play_streak/play_streak_bonus_packer.py
import logging
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.play_streak.play_streak_bonus_model import PlayStreakBonusModel
from gui.impl.gen.view_models.views.lobby.play_streak.play_streak_style_bonus_model import PlayStreakStyleBonusModel
from gui.shared.gui_items.customization.c11n_helpers import getProgressionStyleCamouflage
from gui.shared.gui_items.customization.c11n_helpers import getProgressionStyle
from gui.shared.gui_items.Vehicle import getNationLessName
from gui.shared.missions.packers.bonus import BonusUIPacker, VehiclesBonusUIPacker, TokenBonusUIPacker, StyleProgressBonusUIPacker, getDefaultBonusPackersMap
from gui.server_events.bonuses import C11nProgressTokenBonus
from gui.server_events.awards_formatters import AWARDS_SIZES
from play_streak.play_streak_constants import RANDOM_GOODIE_TOKEN, RANDOM_EQUIPMENT_TOKEN
_logger = logging.getLogger(__name__)

def getPlayStreakBonusPacker():
    mapping = getDefaultBonusPackersMap()
    mapping.update({'vehicles': PlayStreakVehicleBonusUIPacker(),
     C11nProgressTokenBonus.BONUS_NAME: PlayStreakStyleProgressBonusUIPacker(),
     'battleToken': PlayStreakTokenBonusUIPacker()})
    return BonusUIPacker(mapping)


class PlayStreakStyleProgressBonusUIPacker(StyleProgressBonusUIPacker):

    @classmethod
    def _getBonusModel(cls):
        return PlayStreakStyleBonusModel()

    @classmethod
    def _packSingleBonus(cls, bonus):
        model = cls._getBonusModel()
        cls._packCommon(bonus, model)
        styleID = bonus.getStyleID()
        branchID = bonus.getBranchID()
        progressLevel = bonus.getProgressLevel()
        camo = getProgressionStyleCamouflage(styleID, branchID, progressLevel)
        if camo is not None:
            icon = cls._getIcon(styleID, progressLevel)
            label = cls._getLabel(camo)
        else:
            _logger.error('Missing camouflage for StyleProgressBonus: styleID=%s; level=%s', styleID, progressLevel)
            icon = ''
            label = ''
        style = getProgressionStyle(styleID, branchID, progressLevel)
        model.setIcon(icon)
        model.setLabel(label)
        model.setStyleID(styleID)
        model.setStyleCD(style.intCD)
        model.setBranchID(branchID)
        model.setProgressLevel(progressLevel)
        return model

    @staticmethod
    def _getIcon(styleID, progressLevel):
        return 'style_progress_{styleID}_{progressLevel}'.format(styleID=styleID, progressLevel=progressLevel)

    @staticmethod
    def _getLabel(camo):
        return camo.longUserName


class PlayStreakVehicleBonusUIPacker(VehiclesBonusUIPacker):

    @classmethod
    def _getLabel(cls, vehicle):
        return vehicle.shortUserName

    @classmethod
    def _packVehicleBonusModel(cls, bonus, vehInfo, isRent, vehicle):
        model = PlayStreakBonusModel()
        model.setName(cls._createUIName(bonus, isRent))
        model.setIsCompensation(bonus.isCompensation())
        model.setLabel(cls._getLabel(vehicle))
        model.setVehCD(vehicle.intCD)
        model.setVehType(vehicle.type)
        model.setLevel(vehicle.level)
        model.setNation(vehicle.nationName)
        model.setVehName(getNationLessName(vehicle.name))
        model.setIsElite(vehicle.isElite)
        return model


class PlayStreakTokenBonusUIPacker(TokenBonusUIPacker):
    _RANDOM_GOODIE_SOURCE = 'random_goodie'
    _RANDOM_EQUIPMENT_SOURCE = 'random_equipment'

    @classmethod
    def _getTokenBonusType(cls, tokenID, complexToken):
        if tokenID.startswith(RANDOM_GOODIE_TOKEN):
            return RANDOM_GOODIE_TOKEN
        return RANDOM_EQUIPMENT_TOKEN if tokenID.startswith(RANDOM_EQUIPMENT_TOKEN) else super(PlayStreakTokenBonusUIPacker, cls)._getTokenBonusType(tokenID, complexToken)

    @classmethod
    def _getTooltipsPackers(cls):
        packers = super(PlayStreakTokenBonusUIPacker, cls)._getTooltipsPackers()
        packers.update({RANDOM_GOODIE_TOKEN: cls.__getPlayStreakTokenGoodieToolTip})
        return packers

    @classmethod
    def _getTokenBonusPackers(cls):
        tokenBonusPackers = super(PlayStreakTokenBonusUIPacker, cls)._getTokenBonusPackers()
        tokenBonusPackers.update({RANDOM_GOODIE_TOKEN: cls.__packPlayStreakToken(cls._RANDOM_GOODIE_SOURCE),
         RANDOM_EQUIPMENT_TOKEN: cls.__packPlayStreakToken(cls._RANDOM_EQUIPMENT_SOURCE)})
        return tokenBonusPackers

    @classmethod
    def __packPlayStreakToken(cls, name):

        def inner(model, bonus, *args):
            model.setName(name)
            model.setValue(str(bonus.getCount()))
            model.setIconSmall(backport.image(R.images.gui.maps.icons.quests.bonuses.dyn(AWARDS_SIZES.SMALL).dyn(name)()))
            model.setIconBig(backport.image(R.images.gui.maps.icons.quests.bonuses.dyn(AWARDS_SIZES.BIG).dyn(name)()))
            return model

        return inner

    @classmethod
    def __getPlayStreakTokenGoodieToolTip(cls, *_):
        return {'contentId': R.views.lobby.daily.tooltips.RandomGoodieTooltip()}
