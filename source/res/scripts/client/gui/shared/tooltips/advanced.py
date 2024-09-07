# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/advanced.py
from constants import SHELL_TYPES
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.genConsts.FITTING_TYPES import FITTING_TYPES
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from gui.Scaleform.locale.ITEM_TYPES import ITEM_TYPES
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.goodies.goodie_items import DemountKit
from gui.impl import backport
from gui.impl.backport.backport_tooltip import DecoratedTooltipWindow
from gui.impl.gen import R
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.shared.formatters import text_styles
from gui.shared.gui_items.artefacts import OptionalDevice
from gui.shared.tooltips import formatters, ToolTipBaseData
from gui.shared.tooltips.common import BlocksTooltipData
from helpers import dependency
from helpers import i18n
from skeletons.account_helpers.settings_core import ISettingsCore
DISABLED_ITEMS_ID = 12793
CHASSIS_TRACK_WITHIN_TRACK = 'vehicleTrackWithinTrackChassis'
MULTI_TRACK_CHASSIS = 'vehicleMultiTrackChassis'

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
        disabledForWheeled = False
        if self._item is not None:
            if isinstance(self._item, OptionalDevice):
                disabledForWheeled = self._item.intCD == DISABLED_ITEMS_ID
        if disabledForWheeled:
            return []
        else:
            items.extend(self._getBlocksList(*args, **kwargs))
            return items

    def _getBlocksList(self, *args, **kwargs):
        pass

    def _packAdvancedBlocks(self, movie, header, description, descReady=False):
        if not descReady:
            descrTextR = R.strings.tooltips.advanced.dyn(description)
            if descrTextR and descrTextR.isValid():
                descrText = backport.text(descrTextR())
            else:
                descrText = '#tooltips:advanced/' + description
        else:
            descrText = description
        if movie is None:
            items = [formatters.packTextBlockData(text=text_styles.highTitle(header), padding=formatters.packPadding(left=20, top=20)), formatters.packTextBlockData(text=text_styles.main(descrText), padding=formatters.packPadding(left=20, top=10, bottom=20))]
        else:
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
    _MODERN_SUFFIX = '_MODERN'

    def _getBlocksList(self, *args, **kwargs):
        movie = SHELL_MOVIES.get((self._item.type, self._item.isModernMechanics), None)
        header = backport.text(R.strings.tooltips.advanced.header.shellType.dyn(self._item.type, default=R.invalid)())
        description = self._item.type
        if self._item.isModernMechanics:
            description += self._MODERN_SUFFIX
        return self._packAdvancedBlocks(movie, header, description)


class HangarBoosterAdvanced(BaseAdvancedTooltip):

    def _getBlocksList(self, *args, **kwargs):
        item = self._item
        itemId = item.getGUIEmblemID()
        header = self._item.userName
        descReady = False
        if 'crewSkillBattleBooster' in item.tags:
            movie = SKILL_MOVIES[itemId]
            affectedSkillName = item.getAffectedSkillName()
            skillLocales = R.strings.crew_perks.dyn(affectedSkillName)
            itemId = backport.text(skillLocales.shortDescription()) if skillLocales.isValid() else affectedSkillName
            descReady = True
        else:
            movie = MODULE_MOVIES[itemId]
        return self._packAdvancedBlocks(movie, header, itemId, descReady)


class HangarModuleAdvanced(BaseAdvancedTooltip):

    def _getBlocksList(self, *args, **kwargs):
        item = self._item
        itemId = item.getGUIEmblemID()
        movieKey = itemId
        descrKey = itemId
        isEquipment = item.itemTypeName == STORE_CONSTANTS.EQUIPMENT
        isOptionalDevice = item.itemTypeName == STORE_CONSTANTS.OPTIONAL_DEVICE
        if isEquipment or isOptionalDevice:
            header = self._item.shortUserName
        else:
            header = self._item.userType
        if itemId == FITTING_TYPES.VEHICLE_CHASSIS and item.isTrackWithinTrack():
            movieKey = CHASSIS_TRACK_WITHIN_TRACK
            descrKey = CHASSIS_TRACK_WITHIN_TRACK
        if isEquipment:
            if itemId in ('lendLeaseOil', 'qualityOil'):
                descrKey = 'enhancedOil'
            elif item.isStimulator:
                descrKey = 'ration'
        if itemId == FITTING_TYPES.VEHICLE_CHASSIS and item.isMultiTrack():
            movieKey = MULTI_TRACK_CHASSIS
            descrKey = MULTI_TRACK_CHASSIS
        if movieKey not in MODULE_MOVIES:
            movieModule = None
        else:
            movieModule = MODULE_MOVIES[movieKey]
        return self._packAdvancedBlocks(movieModule, header, descrKey)


class TankmanPreviewTooltipAdvanced(BaseAdvancedTooltip):

    def _packBlocks(self, role, *args, **kwargs):
        return self._packAdvancedBlocks(TANKMAN_MOVIES[role], ITEM_TYPES.tankman_roles(role), role)


class VehicleParametersAdvanced(ToolTipBaseData):
    _movies = {'relativePower': 'statFirepower',
     'relativeArmor': 'statSurvivability',
     'relativeMobility': 'statMobility',
     'relativeCamouflage': 'statConcealment',
     'relativeVisibility': 'statSpotting'}

    def __init__(self, context):
        super(VehicleParametersAdvanced, self).__init__(context, None)
        return

    def getDisplayableData(self, paramName, *args, **kwargs):
        from gui.impl.lobby.crew.tooltips.advanced_tooltip_view import AdvancedTooltipView
        return DecoratedTooltipWindow(AdvancedTooltipView(self._movies[paramName], backport.text(R.strings.menu.tank_params.dyn(paramName)()), backport.text(R.strings.tooltips.advanced.dyn(paramName)())), useDecorator=False)


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


class DemountKitTooltipAdvanced(BaseAdvancedTooltip):

    def _packBlocks(self, *args, **kwargs):
        demountKit = self.context.buildItem(*args, **kwargs)
        dkType = demountKit.demountKitGuiType
        return self._packAdvancedBlocks('demountKit', demountKit.userName, 'demountKit/{}'.format(dkType))


SKILL_MOVIES = {'repair': 'skillRepairs',
 'camouflage': 'skillConcealment',
 'naturalCover': 'skillConcealment',
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
 'loader_desperado': 'skillAdrenalineRush',
 'loader_pedant': 'skillSafeStowage',
 'loader_intuition': 'skillIntuition',
 'commander_enemyShotPredictor': 'skillArtLamp'}
MODULE_MOVIES = {'largeRepairkit': 'consumablesRepairKitBig',
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
 'aimingStabilizer': 'equipmentVerticalStabilizer',
 'enhancedAimDrives': 'equipmentGunLayingDrive',
 'coatedOptics': 'equipmentCoatedOptics',
 'stereoscope': 'equipmentBinocularTelescope',
 'camouflageNet': 'equipmentCamouflageNet',
 'antifragmentationLining': 'equipmentLightSpallLiner',
 'improvedVentilation': 'equipmentImprovedVentilation',
 'rammer': 'equipmentMediumCaliberTankGunRammer',
 'vehicleGun': 'moduleGun',
 'vehicleDualGun': 'moduleDualGun',
 'vehicleRadio': 'moduleRadio',
 'vehicleEngine': 'moduleEngine',
 'vehicleChassis': 'moduleSuspension',
 'vehicleWheeledChassis': 'moduleWheel',
 'vehicleTrackWithinTrackChassis': 'moduleTrackWithinTrack',
 'vehicleMultiTrackChassis': 'moduleTrackWithinTrack',
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
 'grousers': 'equipmentAdditionalGrousers',
 'artillery': 'artillery',
 'bomber': 'bomber',
 'inspire': 'inspire',
 'arcade_minefield': 'minefield',
 'stealthRadar': 'patrol',
 'recon': 'recon',
 'regenerationKit': 'resuply',
 'passive_engineering': 'sabotageSquad',
 'smoke': 'smokeCloud',
 'commandersView': 'equipmentCommandersVisionSystem',
 'modernizedAimDrivesAimingStabilizer': 'equipmentExperimentalAiming',
 'modernizedExtraHealthReserveAntifragmentationLining': 'equipmentExperimentalHardening',
 'modernizedTurbochargerRotationMechanism': 'equipmentExperimentalTurbocharger',
 'improvedSights': 'equipmentImprovedAiming',
 'extraHealthReserve': 'equipmentImprovedHardening',
 'improvedRadioCommunication': 'equipmentImprovedRadioSet',
 'improvedRotationMechanism': 'equipmentImprovedRotationMechanism',
 'additionalInvisibilityDevice': 'equipmentLowNoiseExhaustSystem',
 'improvedConfiguration': 'equipmentModifiedConfiguration',
 'turbocharger': 'equipmentTurbocharger'}
TANKMAN_MOVIES = {'commander': 'crewCommander',
 'driver': 'crewDriver',
 'gunner': 'crewGunner',
 'loader': 'crewLoader',
 'radioman': 'crewRadioOperator'}
SHELL_MOVIES = {(SHELL_TYPES.ARMOR_PIERCING, False): 'bulletAP',
 (SHELL_TYPES.HOLLOW_CHARGE, False): 'bulletHEAT',
 (SHELL_TYPES.HIGH_EXPLOSIVE, False): 'bulletHE',
 (SHELL_TYPES.ARMOR_PIERCING_CR, False): 'bulletAPCR',
 (SHELL_TYPES.ARMOR_PIERCING_FSDS, False): 'bulletAPFSDS',
 (SHELL_TYPES.HIGH_EXPLOSIVE, True): 'bulletHEModern',
 (SHELL_TYPES.FLAME, False): 'bulletFlame'}
