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
if typing.TYPE_CHECKING:
    from skeletons.gui.battle_session import IClientArenaVisitor
    from Vehicle import Vehicle
_logger = logging.getLogger(__name__)

class HelpPagePriority(object):
    DEFAULT = 0
    MAPS = 1
    TRACK_WITHIN_TRACK = 2
    ROCKET_ACCELERATION = 3
    TURBOSHAFT_ENGINE = 4
    DUAL_ACCURACY = 5
    AUTO_SHOOT_GUN = 6
    BATTLE_ROYALE = 7
    DUAL_GUN = 8
    WHEELED = 9
    BURNOUT = 10
    SIEGE_MODE = 11
    ROLE_TYPE = 12
    COMP7 = 13
    TWIN_GUN = 14


def addPage(datailedList, headerTitle, title, descr, vKeys, buttons, image, roleImage=None, roleActions=None, hintCtx=None):
    data = {'headerTitle': headerTitle,
     'title': title,
     'descr': descr,
     'vKeys': vKeys,
     'buttons': buttons,
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
        addPage(pages, buildTitle(ctx), backport.text(R.strings.ingame_help.detailsHelp.wheeledVeh.twoModes.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.wheeledVeh.twoModes(), key1=keyName)), [siegeKey], [siegeKeyName], backport.image(R.images.gui.maps.icons.battleHelp.wheeledHelp.wheel_two_mode()), hintCtx=HelpHintContext.MECHANICS)
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
        addPage(pages, buildTitle(ctx), backport.text(R.strings.ingame_help.detailsHelp.wheeledVeh.burnout.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.wheeledVeh.burnout(), key1=keyName1, key2=keyName2)), [forwardKey, breakeKey], [forwardKeyName, breakeKeyName], backport.image(R.images.gui.maps.icons.battleHelp.wheeledHelp.wheel_burnout()), hintCtx=HelpHintContext.MECHANICS)
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
        addPage(pages, headerTitle, backport.text(R.strings.ingame_help.detailsHelp.wheeledVeh.stableChassis.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.wheeledVeh.stableChassis())), [], [], backport.image(R.images.gui.maps.icons.battleHelp.wheeledHelp.wheel_chassis()), hintCtx=HelpHintContext.MECHANICS)
        addPage(pages, headerTitle, backport.text(R.strings.ingame_help.detailsHelp.wheeledVeh.aboutTechnique.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.wheeledVeh.aboutTechnique())), [], [], backport.image(R.images.gui.maps.icons.battleHelp.wheeledHelp.wheel_details()), hintCtx=HelpHintContext.MECHANICS)
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
        addPage(pages, buildTitle(ctx), backport.text(R.strings.ingame_help.detailsHelp.trackWithinTrack.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.trackWithinTrack.description())), [], [], backport.image(R.images.gui.maps.icons.battleHelp.trackWithinTrack.roll_away()), hintCtx=HelpHintContext.MECHANICS)
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
        addPage(pages, headerTitle, backport.text(R.strings.ingame_help.detailsHelp.dualGun.volley_fire.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.dualGun.volley_fire())), [chargeKey], [chargeKeyName], backport.image(R.images.gui.maps.icons.battleHelp.dualGunHelp.volley_fire()), hintCtx=HelpHintContext.MECHANICS)
        addPage(pages, headerTitle, backport.text(R.strings.ingame_help.detailsHelp.dualGun.quick_fire.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.dualGun.quick_fire())), [shootKey], [shootKeyName], backport.image(R.images.gui.maps.icons.battleHelp.dualGunHelp.quick_fire()), hintCtx=HelpHintContext.MECHANICS)
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
        addPage(pages, headerTitle, backport.text(R.strings.ingame_help.detailsHelp.battleRoyale.radar.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.battleRoyale.radar.description())), [], [], backport.image(imagePath.br_radar()), hintCtx=HelpHintContext.BATTLE_ROYALE)
        addPage(pages, headerTitle, backport.text(R.strings.ingame_help.detailsHelp.battleRoyale.zone.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.battleRoyale.zone.description())), [], [], backport.image(imagePath.br_zone()), hintCtx=HelpHintContext.BATTLE_ROYALE)
        addPage(pages, headerTitle, backport.text(R.strings.ingame_help.detailsHelp.battleRoyale.sectorVision.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.battleRoyale.sectorVision.description())), [], [], backport.image(imagePath.br_sector()), hintCtx=HelpHintContext.BATTLE_ROYALE)
        addPage(pages, headerTitle, backport.text(R.strings.ingame_help.detailsHelp.battleRoyale.airDrop.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.battleRoyale.airDrop.description())), [], [], backport.image(imagePath.br_airdrop()), hintCtx=HelpHintContext.BATTLE_ROYALE)
        addPage(pages, headerTitle, backport.text(R.strings.ingame_help.detailsHelp.battleRoyale.upgrade.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.battleRoyale.upgrade.description())), [], [], backport.image(imagePath.br_tree()), hintCtx=HelpHintContext.BATTLE_ROYALE)
        addPage(pages, headerTitle, backport.text(R.strings.ingame_help.detailsHelp.battleRoyale.uniqueAbilities.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.battleRoyale.uniqueAbilities.description())), [], [], backport.image(imagePath.br_unique_abilities()), hintCtx=HelpHintContext.BATTLE_ROYALE)
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
        addPage(pages, headerTitle, backport.text(R.strings.ingame_help.detailsHelp.engineMode.engineModePage1.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.engineMode.engineModePage1())), [siegeKey], [siegeKeyName], backport.image(R.images.gui.maps.icons.battleHelp.turboshaftEngineHelp.engine_mode_page_1()), hintCtx=HelpHintContext.MECHANICS)
        addPage(pages, headerTitle, backport.text(R.strings.ingame_help.detailsHelp.engineMode.engineModePage2.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.engineMode.engineModePage2())), [], [], backport.image(R.images.gui.maps.icons.battleHelp.turboshaftEngineHelp.engine_mode_page_2()), hintCtx=HelpHintContext.MECHANICS)
        return pages

    @classmethod
    def _collectHelpCtx(cls, ctx, arenaVisitor, vehicle):
        ctx['hasTurboshaftEngine'] = hasTurboshaft = vehicle is not None and vehicle.typeDescriptor.hasTurboshaftEngine
        ctx['hasUniqueVehicleHelpScreen'] = ctx.get('hasUniqueVehicleHelpScreen') or hasTurboshaft
        return


class RocketAccelerationPagesBuilder(DetailedHelpPagesBuilder):
    _SUITABLE_CTX_KEYS = ('hasRocketAcceleration',)

    @classmethod
    def priority(cls):
        return HelpPagePriority.ROCKET_ACCELERATION

    @classmethod
    def buildPages(cls, ctx):
        pages = []
        headerTitle = buildTitle(ctx)
        siegeKeyName = getReadableKey(CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION)
        siegeKey = getVirtualKey(CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION)
        addPage(pages, headerTitle, backport.text(R.strings.ingame_help.detailsHelp.rocketAcceleration.page1.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.rocketAcceleration.page1())), [siegeKey], [siegeKeyName], backport.image(R.images.gui.maps.icons.battleHelp.rocketAcceleration.page_1()), hintCtx=HelpHintContext.MECHANICS)
        addPage(pages, headerTitle, backport.text(R.strings.ingame_help.detailsHelp.rocketAcceleration.page2.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.rocketAcceleration.page2())), [], [], backport.image(R.images.gui.maps.icons.battleHelp.rocketAcceleration.page_2()), hintCtx=HelpHintContext.MECHANICS)
        return pages

    @classmethod
    def _collectHelpCtx(cls, ctx, arenaVisitor, vehicle):
        hasRocketAcceleration = vehicle is not None and vehicle.typeDescriptor.hasRocketAcceleration
        ctx['hasUniqueVehicleHelpScreen'] = ctx.get('hasUniqueVehicleHelpScreen') or hasRocketAcceleration
        ctx['hasRocketAcceleration'] = hasRocketAcceleration
        return


class DualAccuracyPagesBuilder(DetailedHelpPagesBuilder):
    _SUITABLE_CTX_KEYS = ('hasDualAccuracy',)

    @classmethod
    def priority(cls):
        return HelpPagePriority.DUAL_ACCURACY

    @classmethod
    def buildPages(cls, ctx):
        pages = []
        addPage(pages, buildTitle(ctx), backport.text(R.strings.ingame_help.detailsHelp.dualAccuracy.mechanics.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.dualAccuracy.mechanics())), [], [], backport.image(R.images.gui.maps.icons.battleHelp.dualAccuracy.mechanics()), hintCtx=HelpHintContext.MECHANICS)
        return pages

    @classmethod
    def _collectHelpCtx(cls, ctx, arenaVisitor, vehicle):
        hasDualAccuracy = vehicle is not None and vehicle.typeDescriptor.hasDualAccuracy
        ctx['hasUniqueVehicleHelpScreen'] = ctx.get('hasUniqueVehicleHelpScreen') or hasDualAccuracy
        ctx['hasDualAccuracy'] = hasDualAccuracy
        return


class AutoShootGunPagesBuilder(DetailedHelpPagesBuilder):
    _SUITABLE_CTX_KEYS = ('isAutoShootGunVehicle',)

    @classmethod
    def priority(cls):
        return HelpPagePriority.AUTO_SHOOT_GUN

    @classmethod
    def buildPages(cls, ctx):
        pages = []
        addPage(pages, buildTitle(ctx), backport.text(R.strings.ingame_help.detailsHelp.autoShootGun.mechanics.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.autoShootGun.mechanics())), [], [], backport.image(R.images.gui.maps.icons.battleHelp.autoShootGun.mechanics()), hintCtx=HelpHintContext.MECHANICS)
        return pages

    @classmethod
    def _collectHelpCtx(cls, ctx, arenaVisitor, vehicle):
        isAutoShootGunVehicle = vehicle is not None and vehicle.typeDescriptor.isAutoShootGunVehicle
        ctx['hasUniqueVehicleHelpScreen'] = ctx.get('hasUniqueVehicleHelpScreen') or isAutoShootGunVehicle
        ctx['isAutoShootGunVehicle'] = isAutoShootGunVehicle
        return


class TwinGunPagesBuilder(DetailedHelpPagesBuilder):
    _SUITABLE_CTX_KEYS = ('isTwinGunVehicle',)

    @classmethod
    def priority(cls):
        return HelpPagePriority.TWIN_GUN

    @classmethod
    def buildPages(cls, ctx):
        pages = []
        headerTitle = buildTitle(ctx)
        addPage(pages, headerTitle, backport.text(R.strings.ingame_help.detailsHelp.twinGun.mechanics.page1.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.twinGun.mechanics.page1())), [getVirtualKey(CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION)], [getReadableKey(CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION)], backport.image(R.images.gui.maps.icons.battleHelp.twinGun.mechanics_page_1()), hintCtx=HelpHintContext.MECHANICS)
        addPage(pages, headerTitle, backport.text(R.strings.ingame_help.detailsHelp.twinGun.mechanics.page2.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.twinGun.mechanics.page2())), [], [], backport.image(R.images.gui.maps.icons.battleHelp.twinGun.mechanics_page_2()), hintCtx=HelpHintContext.MECHANICS)
        return pages

    @classmethod
    def _collectHelpCtx(cls, ctx, arenaVisitor, vehicle):
        isTwinGunVehicle = vehicle is not None and vehicle.typeDescriptor.isTwinGunVehicle
        ctx['hasUniqueVehicleHelpScreen'] = ctx.get('hasUniqueVehicleHelpScreen') or isTwinGunVehicle
        ctx['isTwinGunVehicle'] = isTwinGunVehicle
        return


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
        addPage(pages, backport.text(R.strings.ingame_help.detailsHelp.role.title()), text_styles.superPromoTitle(backport.text(R.strings.menu.roleExp.roleName.dyn(roleTypeLabel)(), groupName=makeHtmlString('html_templates:vehicleRoles', 'roleTitle', {'message': backport.text(R.strings.menu.roleExp.roleGroupName.dyn(roleTypeLabel)())}))), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.role.description())), [], [], backport.image(R.images.gui.maps.icons.battleHelp.rolesHelp.dyn(roleTypeLabel)()), roleImage=backport.image(R.images.gui.maps.icons.roleExp.roles.c_100x100.dyn(roleTypeLabel)()), roleActions=roleActions, hintCtx=HelpHintContext.ROLE_HELP)
        return pages

    @classmethod
    def _collectHelpCtx(cls, ctx, arenaVisitor, vehicle):
        isRanked = arenaVisitor.getArenaGuiType() == ARENA_GUI_TYPE.RANKED
        hasRoleType = isRanked and vehicle is not None and vehicle.typeDescriptor.role != ROLE_TYPE.NOT_DEFINED
        ctx['roleType'] = vehicle.typeDescriptor.role if hasRoleType else ROLE_TYPE.NOT_DEFINED
        return


class Comp7PagesBuilder(DetailedHelpPagesBuilder):
    _SUITABLE_CTX_KEYS = ('isComp7',)

    @classmethod
    def priority(cls):
        return HelpPagePriority.COMP7

    @classmethod
    def buildPages(cls, ctx):
        pages = []
        comp7Header = backport.text(R.strings.comp7.detailsHelp.mainTitle())
        for pageName in ('seasonModifiers', 'poi', 'roleSkills', 'rules'):
            addPage(datailedList=pages, headerTitle=comp7Header, title=backport.text(R.strings.comp7.detailsHelp.dyn(pageName).title()), descr=text_styles.mainBig(backport.text(R.strings.comp7.detailsHelp.dyn(pageName)())), vKeys=[], buttons=[], image=backport.image(R.images.gui.maps.icons.comp7.battleHelp.dyn(pageName)()))

        return pages

    @classmethod
    def _collectHelpCtx(cls, ctx, arenaVisitor, vehicle):
        ctx['isComp7'] = arenaVisitor.getArenaGuiType() in ARENA_GUI_TYPE.COMP7_RANGE


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
        addPage(pages, header, backport.text(cls._STR_PATH.localWeather.title()), text_styles.mainBig(backport.text(cls._STR_PATH.localWeather.description())), [], [], backport.image(R.images.gui.maps.icons.battleHelp.mapbox.localWeather()), hintCtx=hintCtx)
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
        addPage(pages, header, backport.text(cls._STR_PATH.title()), text_styles.mainBig(backport.text(cls._STR_PATH.markers.description())), [], [], backport.image(R.images.gui.maps.icons.battleHelp.devMaps.markers()), hintCtx=hintCtx)
        addPage(pages, header, backport.text(cls._STR_PATH.title()), text_styles.mainBig(backport.text(cls._STR_PATH.zone.description())), [], [], backport.image(R.images.gui.maps.icons.battleHelp.devMaps.zone()), hintCtx=hintCtx)
        return pages

    @classmethod
    def _collectHelpCtx(cls, ctx, arenaVisitor, vehicle):
        ctx['isDevMaps'] = arenaVisitor.extra.isMapsInDevelopmentEnabled()


registerIngameHelpPagesBuilders((SiegeModePagesBuilder,
 BurnOutPagesBuilder,
 WheeledPagesBuilder,
 TrackWithinTrackPagesBuilder,
 DualGunPagesBuilder,
 BattleRoyalePagesBuilder,
 TurboshaftEnginePagesBuilder,
 RoleTypePagesBuilder,
 RocketAccelerationPagesBuilder,
 Comp7PagesBuilder,
 MapboxPagesBuilder,
 AutoShootGunPagesBuilder,
 DualAccuracyPagesBuilder,
 TwinGunPagesBuilder,
 DevMapsPagesBuilder))
