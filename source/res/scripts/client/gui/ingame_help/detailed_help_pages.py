# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/ingame_help/detailed_help_pages.py
import logging
import typing
import CommandMapping
from constants import ARENA_GUI_TYPE, ARENA_BONUS_TYPE, ROLE_TYPE, ACTION_TYPE_TO_LABEL, ROLE_TYPE_TO_LABEL
from gui import makeHtmlString
from gui.Scaleform.daapi.view.battle.shared.hint_panel.hint_panel_plugin import HelpHintContext
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.system_factory import registerIngameHelpPagesBuilders, collectIngameHelpPagesBuilders
from gui.shared.utils.functions import replaceHyphenToUnderscore
from gui.shared.utils.key_mapping import getReadableKey, getVirtualKey
from items.vehicles import getRolesActions
from nations import NAMES as NATIONS_NAMES
from shared_utils import findFirst
from soft_exception import SoftException
from vehicles.mechanics.mechanic_constants import VehicleMechanic
from vehicles.mechanics.mechanic_info import getVehicleMechanics, hasVehicleMechanic
if typing.TYPE_CHECKING:
    from skeletons.gui.battle_session import IClientArenaVisitor
    from Vehicle import Vehicle
_logger = logging.getLogger(__name__)

class HelpPagePriority(object):
    DEFAULT = 0
    MAPS = 1
    TRACK_WITHIN_TRACK = 2
    BATTLE_ROYALE = 3
    TURBOSHAFT_ENGINE = 4
    DUAL_GUN = 5
    WHEELED = 6
    BURNOUT = 7
    SIEGE_MODE = 8
    MECHANICS = 9
    ROLE_TYPE = 10
    PILLBOX_SIEGE = 16


def addPage(datailedList, headerTitle, title, descr, keys, image, roleImage=None, roleActions=None, hintCtx=None):
    data = {'headerTitle': headerTitle,
     'title': title,
     'descr': descr,
     'keys': keys,
     'image': image,
     'roleImage': roleImage,
     'roleActions': roleActions,
     'hintCtx': hintCtx}
    datailedList.append(data)


def buildTitle(ctx):
    title = backport.text(R.strings.ingame_help.detailsHelp.default.title())
    return ctx.get('vehName') or title


def buildPagesData(ctx):
    detailedList = []
    builders = collectIngameHelpPagesBuilders()
    for builder in sorted(builders, key=lambda item: item.priority(), reverse=True):
        if builder.hasPagesForCtx(ctx):
            detailedList.extend(builder.buildPages(ctx))

    selectedIdx = 0
    currentHintCtx = ctx.get('currentHintCtx')
    hintContexts = [ pageData.pop('hintCtx') for pageData in detailedList ]
    if currentHintCtx:
        selected = findFirst(lambda p: p == currentHintCtx, hintContexts)
        if selected is not None:
            selectedIdx = hintContexts.index(selected)
    return (detailedList, selectedIdx)


class DetailedHelpPagesBuilder(object):
    _SUITABLE_CTX_KEYS = ()

    @classmethod
    def hasPagesForCtx(cls, ctx):
        return all((ctx.get(key, False) for key in cls._SUITABLE_CTX_KEYS))

    @classmethod
    def priority(cls):
        return HelpPagePriority.DEFAULT

    @classmethod
    def buildPages(cls, ctx):
        return []

    @classmethod
    def collectHelpCtx(cls, ctx, arenaVisitor, vehicle):
        cls._collectHelpCtx(ctx, arenaVisitor, vehicle)
        return cls.hasPagesForCtx(ctx)

    @classmethod
    def _buildKey(cls, virtualKey, keyName, isLong=False):
        return {'vKey': virtualKey,
         'keyName': keyName,
         'isLong': isLong}

    @classmethod
    def _collectHelpCtx(cls, ctx, arenaVisitor, vehicle):
        raise NotImplementedError


class SiegeModePagesBuilder(DetailedHelpPagesBuilder):
    _SUITABLE_CTX_KEYS = ('isWheeledVehicle', 'hasSiegeMode')

    @classmethod
    def priority(cls):
        return HelpPagePriority.SIEGE_MODE

    @classmethod
    def buildPages(cls, ctx):
        pages = []
        siegeKey = getVirtualKey(CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION)
        siegeKeyName = getReadableKey(CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION)
        keyName = siegeKeyName if siegeKeyName else backport.text(R.strings.ingame_help.detailsHelp.noKey())
        addPage(pages, buildTitle(ctx), backport.text(R.strings.ingame_help.detailsHelp.wheeledVeh.twoModes.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.wheeledVeh.twoModes(), key1=keyName)), [cls._buildKey(siegeKey, siegeKeyName)], backport.image(R.images.gui.maps.icons.battleHelp.wheeledHelp.wheel_two_mode()), hintCtx=HelpHintContext.MECHANICS)
        return pages

    @classmethod
    def _collectHelpCtx(cls, ctx, arenaVisitor, vehicle):
        ctx['hasSiegeMode'] = vehicle is not None and vehicle.typeDescriptor.hasSiegeMode
        ctx['isWheeledVehicle'] = vehicle is not None and vehicle.typeDescriptor.isWheeledVehicle
        return


class BurnOutPagesBuilder(DetailedHelpPagesBuilder):
    _SUITABLE_CTX_KEYS = ('hasBurnout',)

    @classmethod
    def priority(cls):
        return HelpPagePriority.BURNOUT

    @classmethod
    def buildPages(cls, ctx):
        pages = []
        breakeKeyName = getReadableKey(CommandMapping.CMD_BLOCK_TRACKS)
        forwardKeyName = getReadableKey(CommandMapping.CMD_MOVE_FORWARD)
        breakeKey = getVirtualKey(CommandMapping.CMD_BLOCK_TRACKS)
        forwardKey = getVirtualKey(CommandMapping.CMD_MOVE_FORWARD)
        keyName1 = breakeKeyName if breakeKeyName else backport.text(R.strings.ingame_help.detailsHelp.noKey())
        keyName2 = forwardKeyName if forwardKeyName else backport.text(R.strings.ingame_help.detailsHelp.noKey())
        addPage(pages, buildTitle(ctx), backport.text(R.strings.ingame_help.detailsHelp.wheeledVeh.burnout.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.wheeledVeh.burnout(), key1=keyName1, key2=keyName2)), [cls._buildKey(forwardKey, forwardKeyName), cls._buildKey(breakeKey, breakeKeyName)], backport.image(R.images.gui.maps.icons.battleHelp.wheeledHelp.wheel_burnout()), hintCtx=HelpHintContext.MECHANICS)
        return pages

    @classmethod
    def _collectHelpCtx(cls, ctx, arenaVisitor, vehicle):
        ctx['hasBurnout'] = vehicle is not None and vehicle.typeDescriptor.hasBurnout
        return


class WheeledPagesBuilder(DetailedHelpPagesBuilder):
    _SUITABLE_CTX_KEYS = ('isFrenchWheeledVehicle',)

    @classmethod
    def priority(cls):
        return HelpPagePriority.WHEELED

    @classmethod
    def buildPages(cls, ctx):
        headerTitle = buildTitle(ctx)
        pages = []
        addPage(pages, headerTitle, backport.text(R.strings.ingame_help.detailsHelp.wheeledVeh.stableChassis.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.wheeledVeh.stableChassis())), [], backport.image(R.images.gui.maps.icons.battleHelp.wheeledHelp.wheel_chassis()), hintCtx=HelpHintContext.MECHANICS)
        addPage(pages, headerTitle, backport.text(R.strings.ingame_help.detailsHelp.wheeledVeh.aboutTechnique.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.wheeledVeh.aboutTechnique())), [], backport.image(R.images.gui.maps.icons.battleHelp.wheeledHelp.wheel_details()), hintCtx=HelpHintContext.MECHANICS)
        return pages

    @classmethod
    def _collectHelpCtx(cls, ctx, arenaVisitor, vehicle):
        isRoleLtWheeled = vehicle is not None and vehicle.typeDescriptor.role == ROLE_TYPE.LT_WHEELED
        isFrenchWheeledVehicle = isRoleLtWheeled and NATIONS_NAMES[vehicle.typeDescriptor.type.id[0]] == 'france'
        ctx['isFrenchWheeledVehicle'] = isFrenchWheeledVehicle
        ctx['hasUniqueVehicleHelpScreen'] = ctx.get('hasUniqueVehicleHelpScreen') or isFrenchWheeledVehicle
        return


class TrackWithinTrackPagesBuilder(DetailedHelpPagesBuilder):
    _SUITABLE_CTX_KEYS = ('isTrackWithinTrack',)

    @classmethod
    def priority(cls):
        return HelpPagePriority.TRACK_WITHIN_TRACK

    @classmethod
    def buildPages(cls, ctx):
        pages = []
        addPage(pages, buildTitle(ctx), backport.text(R.strings.ingame_help.detailsHelp.trackWithinTrack.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.trackWithinTrack.description())), [], backport.image(R.images.gui.maps.icons.battleHelp.trackWithinTrack.roll_away()), hintCtx=HelpHintContext.MECHANICS)
        return pages

    @classmethod
    def _collectHelpCtx(cls, ctx, arenaVisitor, vehicle):
        ctx['isTrackWithinTrack'] = isTrack = vehicle is not None and vehicle.typeDescriptor.isTrackWithinTrack
        ctx['hasUniqueVehicleHelpScreen'] = ctx.get('hasUniqueVehicleHelpScreen') or isTrack
        return


class DualGunPagesBuilder(DetailedHelpPagesBuilder):
    _SUITABLE_CTX_KEYS = ('isDualGun',)

    @classmethod
    def priority(cls):
        return HelpPagePriority.DUAL_GUN

    @classmethod
    def buildPages(cls, ctx):
        pages = []
        headerTitle = buildTitle(ctx)
        shootKeyName = getReadableKey(CommandMapping.CMD_CM_SHOOT)
        shootKey = getVirtualKey(CommandMapping.CMD_CM_SHOOT)
        chargeKeyName = getReadableKey(CommandMapping.CMD_CM_CHARGE_SHOT)
        chargeKey = getVirtualKey(CommandMapping.CMD_CM_CHARGE_SHOT)
        addPage(pages, headerTitle, backport.text(R.strings.ingame_help.detailsHelp.dualGun.volley_fire.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.dualGun.volley_fire())), [cls._buildKey(chargeKey, chargeKeyName)], backport.image(R.images.gui.maps.icons.battleHelp.dualGunHelp.volley_fire()), hintCtx=HelpHintContext.MECHANICS)
        addPage(pages, headerTitle, backport.text(R.strings.ingame_help.detailsHelp.dualGun.quick_fire.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.dualGun.quick_fire())), [cls._buildKey(shootKey, shootKeyName)], backport.image(R.images.gui.maps.icons.battleHelp.dualGunHelp.quick_fire()), hintCtx=HelpHintContext.MECHANICS)
        return pages

    @classmethod
    def _collectHelpCtx(cls, ctx, arenaVisitor, vehicle):
        ctx['isDualGun'] = isDualGun = vehicle is not None and vehicle.typeDescriptor.isDualgunVehicle
        ctx['hasUniqueVehicleHelpScreen'] = ctx.get('hasUniqueVehicleHelpScreen') or isDualGun
        return


class BattleRoyalePagesBuilder(DetailedHelpPagesBuilder):
    _SUITABLE_CTX_KEYS = ('isBattleRoyale', 'mapGeometryName')

    @classmethod
    def priority(cls):
        return HelpPagePriority.BATTLE_ROYALE

    @classmethod
    def buildPages(cls, ctx):
        pages = []
        headerTitle = backport.text(R.strings.ingame_help.detailsHelp.default.title())
        mapGeometryName = ctx['mapGeometryName']
        mapResourceName = 'c_' + replaceHyphenToUnderscore(mapGeometryName)
        imagePath = R.images.gui.maps.icons.battleHelp.battleRoyale.dyn(mapResourceName)
        if not imagePath.isValid():
            raise SoftException('No icons found for map {}'.format(mapGeometryName))
        addPage(pages, headerTitle, backport.text(R.strings.ingame_help.detailsHelp.battleRoyale.radar.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.battleRoyale.radar.description())), [], backport.image(imagePath.br_radar()), hintCtx=HelpHintContext.BATTLE_ROYALE)
        addPage(pages, headerTitle, backport.text(R.strings.ingame_help.detailsHelp.battleRoyale.zone.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.battleRoyale.zone.description())), [], backport.image(imagePath.br_zone()), hintCtx=HelpHintContext.BATTLE_ROYALE)
        addPage(pages, headerTitle, backport.text(R.strings.ingame_help.detailsHelp.battleRoyale.sectorVision.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.battleRoyale.sectorVision.description())), [], backport.image(imagePath.br_sector()), hintCtx=HelpHintContext.BATTLE_ROYALE)
        addPage(pages, headerTitle, backport.text(R.strings.ingame_help.detailsHelp.battleRoyale.airDrop.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.battleRoyale.airDrop.description())), [], backport.image(imagePath.br_airdrop()), hintCtx=HelpHintContext.BATTLE_ROYALE)
        addPage(pages, headerTitle, backport.text(R.strings.ingame_help.detailsHelp.battleRoyale.upgrade.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.battleRoyale.upgrade.description())), [], backport.image(imagePath.br_tree()), hintCtx=HelpHintContext.BATTLE_ROYALE)
        addPage(pages, headerTitle, backport.text(R.strings.ingame_help.detailsHelp.battleRoyale.uniqueAbilities.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.battleRoyale.uniqueAbilities.description())), [], backport.image(imagePath.br_unique_abilities()), hintCtx=HelpHintContext.BATTLE_ROYALE)
        return pages

    @classmethod
    def _collectHelpCtx(cls, ctx, arenaVisitor, vehicle):
        ctx['isBattleRoyale'] = isRoyale = arenaVisitor.getArenaBonusType() in ARENA_BONUS_TYPE.BATTLE_ROYALE_RANGE
        ctx['hasUniqueVehicleHelpScreen'] = ctx.get('hasUniqueVehicleHelpScreen') or isRoyale
        ctx['mapGeometryName'] = arenaVisitor.type.getGeometryName()


class TurboshaftEnginePagesBuilder(DetailedHelpPagesBuilder):
    _SUITABLE_CTX_KEYS = ('hasTurboshaftEngine',)

    @classmethod
    def priority(cls):
        return HelpPagePriority.TURBOSHAFT_ENGINE

    @classmethod
    def buildPages(cls, ctx):
        pages = []
        headerTitle = buildTitle(ctx)
        siegeKeyName = getReadableKey(CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION)
        siegeKey = getVirtualKey(CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION)
        addPage(pages, headerTitle, backport.text(R.strings.ingame_help.detailsHelp.engineMode.engineModePage1.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.engineMode.engineModePage1())), [cls._buildKey(siegeKey, siegeKeyName)], backport.image(R.images.gui.maps.icons.battleHelp.turboshaftEngineHelp.engine_mode_page_1()), hintCtx=HelpHintContext.MECHANICS)
        addPage(pages, headerTitle, backport.text(R.strings.ingame_help.detailsHelp.engineMode.engineModePage2.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.engineMode.engineModePage2())), [], backport.image(R.images.gui.maps.icons.battleHelp.turboshaftEngineHelp.engine_mode_page_2()), hintCtx=HelpHintContext.MECHANICS)
        return pages

    @classmethod
    def _collectHelpCtx(cls, ctx, arenaVisitor, vehicle):
        ctx['hasTurboshaftEngine'] = hasTurboshaft = vehicle is not None and vehicle.typeDescriptor.hasTurboshaftEngine
        ctx['hasUniqueVehicleHelpScreen'] = ctx.get('hasUniqueVehicleHelpScreen') or hasTurboshaft
        return


class PillboxSiegePagesBuilder(DetailedHelpPagesBuilder):
    _SUITABLE_CTX_KEYS = ('hasPillboxMode',)

    @classmethod
    def priority(cls):
        return HelpPagePriority.PILLBOX_SIEGE

    @classmethod
    def buildPages(cls, ctx):
        pages = []
        headerTitle = buildTitle(ctx)
        pressAndHold = text_styles.hightlight(backport.text(R.strings.ingame_help.detailsHelp.pillboxSiege.mechanics.page1.pressAndHold()))
        description = text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.pillboxSiege.mechanics.page1(), pressAndHold=pressAndHold))
        siegeKey = getVirtualKey(CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION)
        siegeKeyName = getReadableKey(CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION)
        addPage(pages, headerTitle, backport.text(R.strings.ingame_help.detailsHelp.pillboxSiege.mechanics.page1.title()), description, [cls._buildKey(siegeKey, siegeKeyName, True)], backport.image(R.images.gui.maps.icons.battleHelp.pillboxSiege.pillbox_siege_page_1()), hintCtx=HelpHintContext.MECHANICS)
        addPage(pages, headerTitle, backport.text(R.strings.ingame_help.detailsHelp.pillboxSiege.mechanics.page2.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.pillboxSiege.mechanics.page2())), [cls._buildKey(siegeKey, siegeKeyName)], backport.image(R.images.gui.maps.icons.battleHelp.pillboxSiege.pillbox_siege_page_2()), hintCtx=HelpHintContext.MECHANICS)
        return pages

    @classmethod
    def _collectHelpCtx(cls, ctx, arenaVisitor, vehicle):
        ctx['hasPillboxMode'] = hasVehicleMechanic(vehicle.typeDescriptor, VehicleMechanic.PILLBOX_SIEGE_MODE)


class RoleTypePagesBuilder(DetailedHelpPagesBuilder):
    _SUITABLE_CTX_KEYS = ('roleType',)

    @classmethod
    def priority(cls):
        return HelpPagePriority.ROLE_TYPE

    @classmethod
    def buildPages(cls, ctx):
        roleType = ctx.get('roleType')
        roleActions = []
        rolesToActions = getRolesActions()
        for action in rolesToActions[roleType]:
            actionLabel = ACTION_TYPE_TO_LABEL[action]
            roleActions.append({'image': backport.image(R.images.gui.maps.icons.roleExp.actions.c_128x128.dyn(actionLabel)()),
             'description': backport.text(R.strings.menu.roleExp.action.dyn(actionLabel)())})

        roleTypeLabel = ROLE_TYPE_TO_LABEL[roleType]
        pages = []
        addPage(pages, backport.text(R.strings.ingame_help.detailsHelp.role.title()), text_styles.superPromoTitle(backport.text(R.strings.menu.roleExp.roleName.dyn(roleTypeLabel)(), groupName=makeHtmlString('html_templates:vehicleRoles', 'roleTitle', {'message': backport.text(R.strings.menu.roleExp.roleGroupName.dyn(roleTypeLabel)())}))), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.role.description())), [], backport.image(R.images.gui.maps.icons.battleHelp.rolesHelp.dyn(roleTypeLabel)()), roleImage=backport.image(R.images.gui.maps.icons.roleExp.roles.c_100x100.dyn(roleTypeLabel)()), roleActions=roleActions, hintCtx=HelpHintContext.ROLE_HELP)
        return pages

    @classmethod
    def _collectHelpCtx(cls, ctx, arenaVisitor, vehicle):
        isRanked = arenaVisitor.getArenaGuiType() == ARENA_GUI_TYPE.RANKED
        hasRoleType = isRanked and vehicle is not None and vehicle.typeDescriptor.role != ROLE_TYPE.NOT_DEFINED
        ctx['roleType'] = vehicle.typeDescriptor.role if hasRoleType else ROLE_TYPE.NOT_DEFINED
        return


class MapboxPagesBuilder(DetailedHelpPagesBuilder):
    _SUITABLE_CTX_KEYS = ('isMapbox',)
    _STR_PATH = R.strings.ingame_help.detailsHelp.mapbox

    @classmethod
    def priority(cls):
        return HelpPagePriority.MAPS

    @classmethod
    def buildPages(cls, ctx):
        pages = []
        header = backport.text(cls._STR_PATH.headerTitle())
        hintCtx = HelpHintContext.MAPBOX
        addPage(pages, header, backport.text(cls._STR_PATH.localWeather.title()), text_styles.mainBig(backport.text(cls._STR_PATH.localWeather.description())), [], backport.image(R.images.gui.maps.icons.battleHelp.mapbox.localWeather()), hintCtx=hintCtx)
        return pages

    @classmethod
    def _collectHelpCtx(cls, ctx, arenaVisitor, vehicle):
        ctx['isMapbox'] = arenaVisitor.getArenaGuiType() == ARENA_GUI_TYPE.MAPBOX


class DevMapsPagesBuilder(DetailedHelpPagesBuilder):
    _SUITABLE_CTX_KEYS = ('isDevMaps',)
    _STR_PATH = R.strings.ingame_help.detailsHelp.devMaps

    @classmethod
    def priority(cls):
        return HelpPagePriority.MAPS

    @classmethod
    def buildPages(cls, ctx):
        pages = []
        header = backport.text(cls._STR_PATH.headerTitle())
        hintCtx = HelpHintContext.DEV_MAPS
        addPage(pages, header, backport.text(cls._STR_PATH.title()), text_styles.mainBig(backport.text(cls._STR_PATH.markers.description())), [], backport.image(R.images.gui.maps.icons.battleHelp.devMaps.markers()), hintCtx=hintCtx)
        addPage(pages, header, backport.text(cls._STR_PATH.title()), text_styles.mainBig(backport.text(cls._STR_PATH.zone.description())), [], backport.image(R.images.gui.maps.icons.battleHelp.devMaps.zone()), hintCtx=hintCtx)
        return pages

    @classmethod
    def _collectHelpCtx(cls, ctx, arenaVisitor, vehicle):
        ctx['isDevMaps'] = arenaVisitor.extra.isMapsInDevelopmentEnabled()


class MechanicsPagesBuilder(DetailedHelpPagesBuilder):
    _SUITABLE_CTX_KEYS = ('vehicleMechanics',)
    _VEHICLE_MECHANIC_KEYS = {VehicleMechanic.ROCKET_ACCELERATION.value: (CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION, None),
     VehicleMechanic.TWIN_GUN.value: (CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION, None),
     VehicleMechanic.CONCENTRATION_MODE.value: (CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION,),
     VehicleMechanic.SUPPORT_WEAPON.value: (CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION, None),
     VehicleMechanic.RECHARGEABLE_NITRO.value: (CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION, None),
     VehicleMechanic.CHARGE_SHOT.value: (CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION, None),
     VehicleMechanic.STANCE_DANCE.value: (CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION, CommandMapping.CMD_CM_SPECIAL_ABILITY),
     VehicleMechanic.TARGET_DESIGNATOR.value: (CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION, None),
     VehicleMechanic.STATIONARY_RELOAD.value: (CommandMapping.CMD_RELOAD_PARTIAL_CLIP, None)}

    @classmethod
    def priority(cls):
        return HelpPagePriority.MECHANICS

    @classmethod
    def buildPages(cls, ctx):
        pages = []
        headerTitle = buildTitle(ctx)
        mechanics = ctx.get('vehicleMechanics')
        for mechanic in mechanics:
            mechanicValue = mechanic.value
            iconsRoot = R.images.gui.maps.icons.battleHelp.mechanics.dyn(mechanicValue)
            localsRoot = R.strings.ingame_help.detailsHelp.mechanics.dyn(mechanicValue)
            keys = cls._VEHICLE_MECHANIC_KEYS.get(mechanicValue, (None, None))
            for index, (pageID, pageRes) in enumerate(sorted(localsRoot.items())):
                key = keys[index]
                addPage(pages, headerTitle, backport.text(pageRes.title()), text_styles.mainBig(backport.text(pageRes.description())), [cls._buildKey(getVirtualKey(key), getReadableKey(key))] if key is not None else [], backport.image(iconsRoot.dyn(pageID)()), hintCtx=HelpHintContext.MECHANICS)

        return pages

    @classmethod
    def _collectHelpCtx(cls, ctx, arenaVisitor, vehicle):
        ctx['vehicleMechanics'] = getVehicleMechanics(vehicle.typeDescriptor)
        ctx['hasUniqueVehicleHelpScreen'] = ctx.get('hasUniqueVehicleHelpScreen') or bool(ctx['vehicleMechanics'])


registerIngameHelpPagesBuilders((SiegeModePagesBuilder,
 BurnOutPagesBuilder,
 WheeledPagesBuilder,
 TrackWithinTrackPagesBuilder,
 DualGunPagesBuilder,
 BattleRoyalePagesBuilder,
 TurboshaftEnginePagesBuilder,
 RoleTypePagesBuilder,
 MapboxPagesBuilder,
 DevMapsPagesBuilder,
 MechanicsPagesBuilder,
 PillboxSiegePagesBuilder))
