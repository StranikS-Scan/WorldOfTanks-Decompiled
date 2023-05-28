# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_loading/resources/consts.py
import typing
import enum

class EnumWithValues(enum.Enum):

    @classmethod
    def values(cls):
        return [ obj.value for obj in cls.__members__.values() ]


@enum.unique
class ImageVfxs(str, EnumWithValues):
    DUST = 'dust'
    FIRE = 'fire'
    FOG = 'fog'
    RAIN = 'rain'
    SNOW = 'snow'
    SUNSHINE = 'sunshine'


@enum.unique
class LoadingTypes(str, EnumWithValues):
    CLIENT = 'client'
    PLAYER = 'player'


@enum.unique
class MilestonesTypes(str, EnumWithValues):
    CONNECTION = 'connection'
    STANDARD = 'standard'
    BOOTCAMP = 'bootcamp'


@enum.unique
class Milestones(str, EnumWithValues):
    CONNECTION = 'connection'
    ENTER = 'enter'
    INVENTORY = 'inventory'
    SHOP = 'shop'
    DOSSIER = 'dossier'
    DISCOUNTS = 'discounts'
    RECYCLE_BIN = 'recycleBin'
    PLAYER_DATA = 'playerData'
    HANGAR_SPACE = 'loadHangarSpace'
    UPDATE_VEHICLE = 'updateVehicle'
    HANGAR_SPACE_VEHICLE = 'loadHangarSpaceVehicle'
    HANGAR_UI_READY = 'hangarUIReady'
    HANGAR_READY = 'hangarReady'
    LOAD_CONTENT = 'loadContent'
    SYNCHRONIZE = 'synchronize'
    BOOTCAMP_ENQUEUED = 'bootcampEnqueued'


@enum.unique
class InfoStyles(str, EnumWithValues):
    DEFAULT = 'default'
    KOREA = 'korea'
    CHINA = 'china'
