# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/shop/crew.py
import typing
import nations
from gui import GUI_NATIONS
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.gui_items.Tankman import Tankman
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME, VEHICLE_TYPES_ORDER_INDICES
from gui.shared.utils.requesters import RequestCriteria
from gui.shared.utils.requesters.ItemsRequester import PredicateCondition
from items.tankmen import TankmanDescr, generateCompactDescr, getNationConfig
from shared_utils import first
from web.web_client_api.common import TManGender, TManLocation
if typing.TYPE_CHECKING:
    from typing import Generator, Set, Tuple, Union
    from gui.server_events.recruit_helper import _BaseRecruitInfo
    from items.components.tankmen_components import NationConfig, NationGroup
    TManPassport = Tuple[int, bool, bool, str, str, str]
_NEW_SKILL = 'new_skill'
_NEWBIE = 'newbie'
_UNDEFINED = 'undefined'
_EMPTY_STR = ''
_INVALID_VALUE = -1

class ShopCrewCriteria(object):
    PREMIUM = RequestCriteria(PredicateCondition(lambda item: item.isPremium))


class _ShopTankman(object):

    def __init__(self, tankman):
        self.__tankman = tankman

    def __getattr__(self, name):
        return getattr(self.__tankman, name)

    @property
    def isPremium(self):
        return self.descriptor.isPremium

    @property
    def location(self):
        if self.isDismissed:
            return TManLocation.DEMOBILIZED
        return TManLocation.TANKS if self.isInTank else TManLocation.BARRACKS

    @property
    def roleID(self):
        return Tankman.TANKMEN_ROLES_ORDER[self.role]

    @property
    def roleName(self):
        return self.__tankman.role

    @property
    def gender(self):
        return TManGender.FEMALE if self.isFemale else TManGender.MALE

    @property
    def groupName(self):
        return self._getNationGroup(self.nationID, self.isPremium, self.descriptor.gid).name

    @property
    def nationName(self):
        return nations.MAP[self.nationID]

    @property
    def nationUserName(self):
        return backport.text(R.strings.nations.dyn(self.nationName)())

    @property
    def rankID(self):
        return self.descriptor.rankID

    @staticmethod
    def _getNationGroup(nationID, isPremium, groupID):
        config = getNationConfig(nationID)
        return (config.premiumGroups if isPremium else config.normalGroups).get(groupID)


class _ShopRecruit(_ShopTankman):
    __R_CREW = R.strings.quests.bonuses.item

    @property
    def location(self):
        return TManLocation.NEWBIES

    @property
    def roleID(self):
        return _INVALID_VALUE

    @property
    def roleName(self):
        return _NEWBIE

    @property
    def roleUserName(self):
        return self.__getNewbieStr()

    @property
    def groupName(self):
        return self._getNationGroup(self.descriptor.nationID, self.isPremium, self.descriptor.gid).name

    @property
    def nationID(self):
        return nations.NONE_INDEX

    @property
    def nationName(self):
        return _EMPTY_STR

    @property
    def nationUserName(self):
        return _EMPTY_STR

    @property
    def rankID(self):
        return _INVALID_VALUE

    @property
    def rankUserName(self):
        return self.__getNewbieStr()

    @property
    def vehicleNativeDescr(self):
        return None

    @property
    def iconRank(self):
        return _EMPTY_STR

    @property
    def iconRole(self):
        return _EMPTY_STR

    def __getNewbieStr(self):
        return backport.text(self.__R_CREW.tankwoman() if self.isFemale else self.__R_CREW.tankman())


def makeTankman(crewItem):
    return _ShopTankman(crewItem) if isinstance(crewItem, Tankman) else _ShopRecruit(_recruit(crewItem))


def _recruit(recruitInfo):
    iterNationGroups = ((nationID, set(_iterNationGroups(config, recruitInfo.getIsPremium(), recruitInfo.getGroupName()))) for nationID, config in _iterNationsConfigs())
    currentNationGroup = first(((nationID, first(nationGroups)) for nationID, nationGroups in iterNationGroups if nationGroups))
    return Tankman(TankmanDescr(generateCompactDescr(passport=_makePassport(recruitInfo, currentNationGroup), vehicleTypeID=VEHICLE_TYPES_ORDER_INDICES[VEHICLE_CLASS_NAME.MEDIUM_TANK], role=Tankman.ROLES.COMMANDER, roleLevel=recruitInfo.getRoleLevel(), skills=[ s for s in recruitInfo.getLearntSkills() if s != _NEW_SKILL ], lastSkillLevel=recruitInfo.getLastSkillLevel())).makeCompactDescr())


def _iterNationGroups(config, isPremium, groupName):
    iterGroups = (config.premiumGroups if isPremium else config.normalGroups).itervalues()
    return (group for group in iterGroups if group.name == groupName)


def _iterNationsConfigs():
    return ((nationID, getNationConfig(nationID)) for nationID in (nations.NAMES.index(n) for n in GUI_NATIONS))


def _makePassport(recruitInfo, nationGroup):
    nationID, group = nationGroup
    return (nationID,
     recruitInfo.getIsPremium(),
     recruitInfo.isFemale(),
     first(group.firstNames),
     first(group.lastNames),
     first(group.icons))
