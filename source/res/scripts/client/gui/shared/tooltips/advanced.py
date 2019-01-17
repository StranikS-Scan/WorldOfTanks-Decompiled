# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/advanced.py
from constants import SHELL_TYPES
from helpers.i18n import makeString
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from CurrentVehicle import g_currentVehicle
from gui.shared.formatters import text_styles
from gui.shared.tooltips.common import BlocksTooltipData
from gui.shared.tooltips import formatters
from gui.shared.items_parameters import formatters as param_formatter
from gui.shared.gui_items.vehicle_modules import VehicleChassis
from gui.shared.gui_items.artefacts import OptionalDevice
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.ITEM_TYPES import ITEM_TYPES
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from helpers import i18n
DISABLED_ITEMS_IDS = (12793, 37954, 40258, 38722, 38210, 39234, 40514, 39746, 38978, 38466, 39490, 40002)

class ComplexTooltip(BlocksTooltipData):
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, context, disableAnim):
        super(ComplexTooltip, self).__init__(context, None)
        self._setMargins(11, 14)
        self._setWidth(520)
        self._disableAnim = disableAnim
        return

    def _packBlocks(self, *args, **kwargs):
        items = super(ComplexTooltip, self)._packBlocks(*args, **kwargs)
        strs = args[0].split('<br/>')
        items.append(formatters.packImageTextBlockData(title=strs[0], desc=strs[1]))
        block = formatters.packImageTextBlockData(img=RES_ICONS.MAPS_ICONS_LOBBY_ICONBTNALT, txtOffset=40, padding=formatters.packPadding(bottom=-7, top=-5, left=20 - self._getContentMargin()['left']), desc=text_styles.main(TOOLTIPS.ADVANCED_INFO), linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_ADVANCED_KEY_BLOCK_LINKAGE)
        block['data']['animated'] = not self._disableAnim
        items.append(block)
        return items


class BaseAdvancedTooltip(BlocksTooltipData):

    def __init__(self, context):
        super(BaseAdvancedTooltip, self).__init__(context, None)
        self._setContentMargin(top=2, left=3, bottom=3, right=3)
        self._setMargins(afterBlock=0)
        self._setWidth(415)
        self._item = None
        return

    @staticmethod
    def getMovieAnimationPath(moviename):
        return 'animations/advancedHints/%s.swf' % moviename

    def _packBlocks(self, *args, **kwargs):
        from debug_utils import LOG_DEBUG
        LOG_DEBUG('packBlocks::', args, kwargs, self.context)
        self._item = self.context.buildItem(*args, **kwargs)
        items = super(BaseAdvancedTooltip, self)._packBlocks()
        if self._item is not None and isinstance(self._item, VehicleChassis) or isinstance(self._item, OptionalDevice):
            disabledForWheeled = g_currentVehicle.item.isWheeledTech and self._item.intCD in DISABLED_ITEMS_IDS
            if disabledForWheeled:
                return []
        items.extend(self._getBlocksList(*args, **kwargs))
        return items

    def _getBlocksList(self, *args, **kwargs):
        pass

    def _packAdvancedBlocks(self, movie, header, description):
        descrText = TOOLTIPS.getAdvancedDescription(description)
        if descrText is None:
            descrText = '#advanced/' + description
        items = [formatters.packTextBlockData(text=text_styles.highTitle(header), padding=formatters.packPadding(left=20, top=20)), formatters.packImageBlockData(BaseAdvancedTooltip.getMovieAnimationPath(movie), BLOCKS_TOOLTIP_TYPES.ALIGN_LEFT, padding=5, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_ADVANCED_CLIP_BLOCK_LINKAGE), formatters.packTextBlockData(text=text_styles.main(descrText), padding=formatters.packPadding(left=20, top=10, bottom=20))]
        return items


class FakeAdvancedTooltip(BaseAdvancedTooltip):

    def _getBlocksList(self, *args, **kwargs):
        return []


class ComplexAdvanced(BaseAdvancedTooltip):

    def _getBlocksList(self, item, *args, **kwargs):
        text, linkage = item
        headerKey = '#tooltips:advanced/{}/header'.format(text)
        if headerKey in TOOLTIPS.ADVANCED_ENUM:
            header = headerKey
        else:
            header = linkage + '/header'
        return self._packAdvancedBlocks(text, header, text)


class HangarShellAdvanced(BaseAdvancedTooltip):
    _shellMovies = {SHELL_TYPES.ARMOR_PIERCING: 'bulletAP',
     SHELL_TYPES.HOLLOW_CHARGE: 'bulletHEAT',
     SHELL_TYPES.HIGH_EXPLOSIVE: 'bulletHE',
     SHELL_TYPES.ARMOR_PIERCING_CR: 'bulletAPCR'}

    def _getBlocksList(self, *args, **kwargs):
        header = makeString(TOOLTIPS.getAdvancedHeaderShellType(self._item.type))
        return self._packAdvancedBlocks(HangarShellAdvanced._shellMovies[self._item.type], header, self._item.type)


class HangarBoosterAdvanced(BaseAdvancedTooltip):

    def _getBlocksList(self, *args, **kwargs):
        item = self._item
        itemId = item.getGUIEmblemID()
        header = self._item.userName
        if 'crewSkillBattleBooster' in item.tags:
            movie = _SKILL_MOVIES[itemId]
        else:
            movie = _MODULE_MOVIES[itemId]
        return self._packAdvancedBlocks(movie, header, itemId)


class HangarModuleAdvanced(BaseAdvancedTooltip):

    def _getBlocksList(self, *args, **kwargs):
        item = self._item
        itemId = item.getGUIEmblemID()
        isEquipment = item.itemTypeName == STORE_CONSTANTS.EQUIPMENT
        isOptionalDevice = item.itemTypeName == STORE_CONSTANTS.OPTIONAL_DEVICE
        if isEquipment or isOptionalDevice:
            header = self._item.shortUserName
        else:
            header = self._item.userType
        movieKey = itemId
        descrKey = itemId
        if movieKey not in _MODULE_MOVIES:
            movieModule = None
        else:
            movieModule = _MODULE_MOVIES[movieKey]
        if isEquipment:
            if itemId in ('lendLeaseOil', 'qualityOil'):
                descrKey = 'enhancedOil'
            elif item.isStimulator:
                descrKey = 'ration'
        return self._packAdvancedBlocks(movieModule, header, descrKey)


class TankmanPreviewTooltipAdvanced(BaseAdvancedTooltip):

    def _packBlocks(self, role):
        return self._packAdvancedBlocks(_TANKMAN_MOVIES[role], ITEM_TYPES.tankman_roles(role), role)


class TankmanTooltipAdvanced(BaseAdvancedTooltip):

    def _getBlocksList(self, *args, **kwargs):
        return self._packAdvancedBlocks(_TANKMAN_MOVIES[self._item.role], self._item.roleUserName, self._item.role)


class SkillTooltipAdvanced(BaseAdvancedTooltip):

    def _getBlocksList(self, *args, **kwargs):
        return self._packAdvancedBlocks(_SKILL_MOVIES[self._item.name], self._item.userName, self._item.name)


class SkillExtendedTooltipAdvanced(BaseAdvancedTooltip):

    def _getBlocksList(self, *args, **kwargs):
        skillType = args[0]
        return self._packAdvancedBlocks(_SKILL_MOVIES[skillType], TOOLTIPS.skillTooltipHeader(skillType), skillType)


class VehicleParametersAdvanced(BaseAdvancedTooltip):
    _movies = {'relativePower': 'statFirepower',
     'relativeArmor': 'statSurvivability',
     'relativeMobility': 'statMobility',
     'relativeCamouflage': 'statConcealment',
     'relativeVisibility': 'statSpotting'}

    def _getBlocksList(self, paramName, *args, **kwargs):
        return self._packAdvancedBlocks(VehicleParametersAdvanced._movies[paramName], MENU.tank_params(paramName), paramName)

    @staticmethod
    def readyForAdvanced(*args, **_):
        return param_formatter.isRelativeParameter(args[0])


class MoneyAndXpAdvanced(BaseAdvancedTooltip):
    _moviesOrDescriptions = {'crystal': 'economyBonds',
     'credits': 'economyCredits',
     'gold': 'economyGold',
     'freeXP': 'economyConvertExp'}

    def _getBlocksList(self, *args, **kwargs):
        _type = args[0]
        movie = self._moviesOrDescriptions[_type]
        header = TOOLTIPS.getHeaderBtnTitle(_type)
        description = self._moviesOrDescriptions[_type]
        return self._packAdvancedBlocks(movie, header, description)


class RankedAdvanced(BaseAdvancedTooltip):

    def _getBlocksList(self, *args, **kwargs):
        return self._packAdvancedBlocks('gamemodeRanked', i18n.makeString(TOOLTIPS.BATTLETYPES_RANKED + '/header'), PREBATTLE_ACTION_NAME.RANKED)


class BattleTraining(BaseAdvancedTooltip):

    def _getBlocksList(self, *args, **kwargs):
        return self._packAdvancedBlocks('gamemodeProving', TOOLTIPS.BATTLETYPES_BATTLETEACHING_HEADER, PREBATTLE_ACTION_NAME.SANDBOX)


_SKILL_MOVIES = {'repair': 'skillRepairs',
 'camouflage': 'skillConcealment',
 'fireFighting': 'skillFirefighting',
 'brotherhood': 'skillBrothersInArms',
 'commander_tutor': 'skillMentor',
 'commander_eagleEye': 'skillEagleEye',
 'commander_universalist': 'skillJackOfAllTrades',
 'commander_expert': 'skillExpert',
 'commander_sixthSense': 'skillSixthSense',
 'gunner_rancorous': 'skillDesignatedTarget',
 'gunner_gunsmith': 'skillArmorer',
 'gunner_sniper': 'skillDeadEye',
 'gunner_smoothTurret': 'skillSnapShot',
 'driver_rammingMaster': 'skillControlledImpact',
 'driver_badRoadsKing': 'skillOffRoadDriving',
 'driver_tidyPerson': 'skillPreventativeMaintenance',
 'driver_virtuoso': 'skillClutchBraking',
 'driver_smoothDriving': 'skillSmoothRide',
 'radioman_finder': 'skillSituationalAwareness',
 'radioman_lastEffort': 'skillCallForVengeance',
 'radioman_inventor': 'skillSignalBoosting',
 'radioman_retransmitter': 'skillRelaying',
 'loader_intuition': 'skillIntuition',
 'loader_desperado': 'skillAdrenalineRush',
 'loader_pedant': 'skillSafeStowage'}
_MODULE_MOVIES = {'largeRepairkit': 'consumablesRepairKitBig',
 'smallRepairkit': 'consumablesRepairKitSmall',
 'largeMedkit': 'consumablesFirstAidBig',
 'smallMedkit': 'consumablesFirstAidSmall',
 'autoExtinguishers': 'consumablesExtinguisherBig',
 'handExtinguishers': 'consumablesExtinguisherSmall',
 'lendLeaseOil': 'consumablesOilLendLease',
 'qualityOil': 'consumablesOilQuality',
 'removedRpmLimiter': 'consumablesSpeedGovernorRemoved',
 'gasoline105': 'consumablesGasoline105',
 'gasoline100': 'consumablesGasoline100',
 'toolbox': 'equipmentToolbox',
 'aimingStabilizer': 'equipmentVerticalStabilizer',
 'carbonDioxide': 'equipmentCO2',
 'enhancedAimDrives': 'equipmentGunLayingDrive',
 'coatedOptics': 'equipmentCoatedOptics',
 'stereoscope': 'equipmentBinocularTelescope',
 'camouflageNet': 'equipmentCamouflageNet',
 'steelRollers': 'equipmentEnhancedSuspension',
 'antifragmentationLining': 'equipmentLightSpallLiner',
 'improvedVentilation': 'equipmentImprovedVentilation',
 'wetCombatPack': 'equipmentWetAmmoRack',
 'filterCyclone': 'equipmentCycloneFilter',
 'rammer': 'equipmentMediumCaliberTankGunRammer',
 'vehicleGun': 'moduleGun',
 'vehicleRadio': 'moduleRadio',
 'vehicleEngine': 'moduleEngine',
 'vehicleChassis': 'moduleSuspension',
 'vehicleTurret': 'moduleTurret',
 'cocacola': 'consumablesCola',
 'chocolate': 'consumablesChocolate',
 'ration': 'consumablesExtraCombatRations',
 'hotCoffee': 'consumablesStrongCoffee',
 'ration_china': 'consumablesImprovedCombatRations',
 'ration_uk': 'consumablesPuddingAndTea',
 'ration_japan': 'consumablesOnigiri',
 'ration_czech': 'consumablesBuchty',
 'ration_sweden': 'consumablesCoffeeWithCinnamonBuns',
 'ration_poland': 'consumablesBreadWithSchmaltz',
 'ration_italy': 'consumablesSpaghetti',
 'grousers': 'equipmentAdditionalGrousers'}
_TANKMAN_MOVIES = {'commander': 'crewCommander',
 'driver': 'crewDriver',
 'gunner': 'crewGunner',
 'loader': 'crewLoader',
 'radioman': 'crewRadioOperator'}
