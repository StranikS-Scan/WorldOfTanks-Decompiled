# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/paragons/paragons_bonuses_packers.py
import typing
from constants import ROLE_TYPE_TO_LABEL
from gui.Scaleform.daapi.view.lobby.server_events.awards_formatters import SimpleBonusFormatter
from gui.impl import backport
from gui.impl.backport import TooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.common.missions.bonuses.token_bonus_model import TokenBonusModel
from gui.server_events.awards_formatters import AwardsPacker, QuestsBonusComposer
from gui.server_events.bonuses import SimpleBonus
from gui.server_events.recruit_helper import getRecruitInfo
from gui.shared.missions.packers.bonus import SimpleBonusUIPacker, TmanTemplateBonusPacker, getDefaultBonusPackersMap, BonusUIPacker, StyleProgressBonusUIPacker
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.gen.view_models.views.lobby.paragons.common.paragons_vehicle_model import ParagonsVehicleModel, VehicleType
from gui.impl.gen.view_models.views.lobby.paragons.common.paragons_unlock_model import ParagonsUnlockModel
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel
from gui.shared.gui_items.customization.c11n_helpers import getProgressionStyle
from gui.shared.missions.packers.bonus import VehiclesBonusUIPacker
from gui.shared.gui_items.Vehicle import getNationLessName
from gui.shared.gui_items.customization import CustomizationTooltipContext
from items.tankmen import RECRUIT_TMAN_TOKEN_PREFIX
if typing.TYPE_CHECKING:
    from gui.server_events.bonuses import TmanTemplateTokensBonus
    from gui.server_events.bonuses import C11nProgressTokenBonus

def getParagonsBonusPacker():
    mapping = getDefaultBonusPackersMap()
    mapping.update({'tmanToken': ParagonsTmanBonusUIPacker,
     'styleProgress': ParagonsProgressStyleBonusUIPacker,
     'paragonsUnlocks': ParagonsUnlockBonusUIPacker,
     'vehicleSelector': ParagonsVehicleSelectorBonusUIPacker,
     'vehicles': ParagonsVehicleBonusUIPacker})
    return BonusUIPacker(mapping)


class ParagonsVehicleSelectorBonusUIPacker(SimpleBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        return [cls._packParagonsVehicleSelectorBonus(cls._getBonusModel(), bonus, bonus.getName())]

    @classmethod
    def _packParagonsVehicleSelectorBonus(cls, model, bonus, label):
        cls._packCommon(bonus, model)
        model.setValue(str(bonus.getValue().keys()[0]))
        model.setIcon('vehicleSelect')
        model.setName('vehicleSelect')
        return model

    @classmethod
    def _getBonusModel(cls):
        return IconBonusModel()

    @classmethod
    def _getContentId(cls, bonus):
        return [R.views.lobby.paragons.tooltips.VehicleSelectTooltip()]

    @classmethod
    def _getToolTip(cls, bonus):
        return [TooltipData(tooltip=None, isSpecial=True, specialAlias=bonus.getName(), specialArgs=[bonus.getValue()])]


class ParagonsVehicleBonusUIPacker(VehiclesBonusUIPacker):

    @classmethod
    def _packVehicleBonusModel(cls, bonus, vehInfo, isRent, vehicle):
        model = ParagonsVehicleModel()
        model.setName(bonus.getName())
        model.setVehicleName(getNationLessName(vehicle.name))
        model.setType(VehicleType(vehicle.type))
        model.setNationTag(vehicle.nationName)
        model.setLevel(vehicle.level)
        model.setIsCompensation(bonus.isCompensation())
        model.setIsElite(vehicle.isElite)
        model.setIsRent(vehicle.isRented)
        model.setInInventory(vehicle.isInInventory)
        model.setWasSold(vehicle.restoreInfo is not None)
        model.setVehicleCD(vehicle.intCD)
        if isRent:
            model.setRentDays(bonus.getRentDays(vehInfo) or 0)
            model.setRentBattles(bonus.getRentBattles(vehInfo) or 0)
        model.setLabel(cls._getLabel(vehicle))
        model.setShortVehicleLabel(vehicle.shortUserName)
        model.setRole(ROLE_TYPE_TO_LABEL.get(vehicle.descriptor.type.role, ''))
        return model


class ParagonsUnlockBonusUIPacker(SimpleBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        return [cls._packParagonsUnlockBonus(bonus, bonus.getName())]

    @classmethod
    def _packParagonsUnlockBonus(cls, bonus, label):
        model = cls._getBonusModel()
        cls._packCommon(bonus, model)
        bonusCtx = bonus.getContext()
        model.setLabel(backport.text(R.strings.paragons.rewards.paragonsUnlock()))
        model.setIcon('branch')
        model.setIsLocked(bonusCtx.get('isLocked', False))
        model.setId(next(iter(bonus.getValue().get('ids'))))
        return model

    @classmethod
    def _getBonusModel(cls):
        return ParagonsUnlockModel()

    @classmethod
    def _getContentId(cls, bonus):
        return [R.views.lobby.paragons.tooltips.BranchSelectTooltip()]

    @classmethod
    def _getToolTip(cls, bonus):
        return [TooltipData(tooltip=None, isSpecial=True, specialAlias=bonus.getName(), specialArgs=[next(iter(bonus.getValue().get('ids')))])]


class ParagonsProgressStyleBonusUIPacker(StyleProgressBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus):
        model = cls._getBonusModel()
        cls._packCommon(bonus, model)
        styleID = bonus.getStyleID()
        branchID = bonus.getBranchID()
        progressLevel = bonus.getProgressLevel()
        model.setIcon(cls.__getIcon(styleID, progressLevel))
        model.setLabel(bonus.format())
        model.setStyleID(styleID)
        model.setBranchID(branchID)
        model.setProgressLevel(progressLevel)
        return model

    @staticmethod
    def __getIcon(styleID, progressLevel):
        return 'style_progress_{styleID}_{progressLevel}'.format(styleID=styleID, progressLevel=progressLevel)

    @staticmethod
    def __getLabel(camo):
        return camo.longUserName

    @classmethod
    def _getToolTip(cls, bonus):
        styleID = bonus.getStyleID()
        branchID = bonus.getBranchID()
        progressLevel = bonus.getProgressLevel()
        style = getProgressionStyle(styleID, branchID, progressLevel)
        tooltipData = TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_AWARD, specialArgs=CustomizationTooltipContext(itemCD=style.intCD, showStatusBlock=False))
        return [tooltipData]


class ParagonsTmanBonusUIPacker(TmanTemplateBonusPacker):

    @classmethod
    def _pack(cls, bonus):
        result = []
        for tokenID in bonus.getTokens().iterkeys():
            if tokenID.startswith(RECRUIT_TMAN_TOKEN_PREFIX):
                packed = cls._packTmanTemplateToken(tokenID, bonus)
                if packed is not None:
                    result.append(packed)

        return result

    @classmethod
    def _packTmanTemplateToken(cls, tokenID, bonus):
        recruitInfo = getRecruitInfo(tokenID)
        if recruitInfo is None:
            return
        else:
            model = TokenBonusModel()
            cls._packCommon(bonus, model)
            tokenRecord = bonus.getTokens()[tokenID]
            if tokenRecord.count > 1:
                model.setValue(str(tokenRecord.count))
            model.setLabel(backport.text(R.strings.paragons.rewards.tman(), tmanName=recruitInfo.getFullUserName()))
            model.setIcon(recruitInfo.getSourceID())
            model.setUserName(recruitInfo.getFullUserName())
            return model


def _formatDossier(bonus):
    return [ backport.text(R.strings.quests.bonuses.dossier.achive(), name=name) for name in bonus.formattedList() ]


def _formatCustomizations(bonus):
    return [] if any((bonus.getC11nItem(item).isQuestsProgression for item in bonus.getCustomizations())) else bonus.formattedList()


class ParagonsTextPostBattleBonusFormatter(SimpleBonusFormatter):
    _UNIQUE_FORMATTER = {'dossier': _formatDossier,
     'customizations': _formatCustomizations}

    def accumulateBonuses(self, bonus, event=None):
        formattedList = self._UNIQUE_FORMATTER.get(bonus.getName(), lambda b: b.formattedList())(bonus)
        if formattedList:
            self._result.extend(formattedList)


class ParagonsPostBattleBonusesPacker(AwardsPacker):
    _ORDER = {k:v for v, k in enumerate(('vehicles', 'styleProgress', 'tmanToken', 'paragonsUnlocks', 'entitlements'))}

    def __init__(self):
        super(ParagonsPostBattleBonusesPacker, self).__init__()
        self.__bonusFormatter = ParagonsTextPostBattleBonusFormatter()

    def format(self, bonuses, event=None):
        for b in sorted(bonuses, key=lambda k: self._ORDER.get(k.getName(), len(self._ORDER))):
            if b.isShowInGUI():
                self.__bonusFormatter.accumulateBonuses(b)

        return self.__bonusFormatter.extractFormattedBonuses()


def packBonusesForPostBattle(bonuses):
    return QuestsBonusComposer(ParagonsPostBattleBonusesPacker()).getPreformattedBonuses(bonuses)
