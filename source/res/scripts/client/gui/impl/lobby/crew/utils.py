# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/utils.py
import itertools
import typing
from collections import namedtuple
import SoundGroups
import nations
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.common.filter_toggle_group_model import ToggleGroupType
from gui.impl.gen.view_models.views.lobby.crew.common.info_tip_model import InfoTipModel
from gui.impl.gen.view_models.views.lobby.crew.popovers.filter_popover_view_model import VehicleSortColumn
from gui.impl.gen.view_models.views.lobby.crew.tankman_model import TankmanLocation
from gui.impl.lobby.crew.filter import GRADE_PREMIUM, GRADE_ELITE, GRADE_PRIMARY
from gui.shared.gui_items.Vehicle import VEHICLE_TYPES_ORDER_INDICES, VEHICLE_TAGS
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import strcmp
from shared_utils import CONST_CONTAINER
if typing.TYPE_CHECKING:
    from gui.shared.utils.requesters import RequestCriteria
    from typing import Dict, Set
VEHICLE_TAGS_FILTER = (VEHICLE_TAGS.PREMIUM_IGR, VEHICLE_TAGS.WOT_PLUS)
DocumentRecord = namedtuple('DocumentRecord', ['id', 'group', 'value'])

class TRAINING_TIPS(CONST_CONTAINER):
    CHOOSE_ANY_CREW_MEMBER = 'chooseAnyCrewMember'
    MAXED_CREW_MEMBERS = 'maxedCrewMembers'
    ENOUGH_EXPERIENCE = 'enoughExperience'
    NOT_SUITABLE_CREW = 'notSuitableCrew'
    NOT_ALL_CURRENT_CREW = 'notAllCurrentCrew'
    tips = {CHOOSE_ANY_CREW_MEMBER: 1,
     MAXED_CREW_MEMBERS: 2,
     ENOUGH_EXPERIENCE: 3,
     NOT_SUITABLE_CREW: 11,
     NOT_ALL_CURRENT_CREW: 12}


def getTip(tipID, tipType, vehName=None):
    tip = InfoTipModel()
    tip.setId(TRAINING_TIPS.tips[tipID])
    tip.setText(backport.text(R.strings.tooltips.quickTraining.dyn(tipID)(), vehName=vehName))
    tip.setType(tipType)
    return tip


def buildPopoverTankFilterCriteria(filters):
    criteria = REQ_CRITERIA.UNLOCKED
    criteria |= REQ_CRITERIA.INVENTORY
    criteria |= ~REQ_CRITERIA.VEHICLE.IS_CREW_LOCKED
    criteria |= ~REQ_CRITERIA.VEHICLE.EVENT_BATTLE
    criteria |= ~REQ_CRITERIA.VEHICLE.BATTLE_ROYALE
    for field, value in filters.items():
        if not value:
            continue
        if field == ToggleGroupType.NATION.value:
            criteria |= REQ_CRITERIA.NATIONS(tuple((nations.INDICES[item] for item in value)))
        if field == ToggleGroupType.VEHICLETYPE.value and value:
            criteria |= REQ_CRITERIA.VEHICLE.CLASSES(tuple(value))
        if field == ToggleGroupType.TANKMANROLE.value and value:
            roleCriteria = REQ_CRITERIA.NONE
            for role in value:
                roleCriteria ^= REQ_CRITERIA.VEHICLE.HAS_ROLE(role)

            criteria |= roleCriteria
        if field == ToggleGroupType.VEHICLETIER.value and value:
            criteria |= REQ_CRITERIA.VEHICLE.LEVELS(tuple((int(item) for item in value)))
        if field == ToggleGroupType.VEHICLEGRADE.value and value:
            value = value - {TankmanLocation.INTANK.value, TankmanLocation.INBARRACKS.value}
            if not value:
                continue
            gradeCriteria = REQ_CRITERIA.NONE
            if GRADE_PREMIUM in value:
                gradeCriteria ^= REQ_CRITERIA.VEHICLE.PREMIUM
            if GRADE_ELITE in value:
                gradeCriteria ^= REQ_CRITERIA.CUSTOM(lambda vehicle: vehicle.isElite and not vehicle.isPremium)
            if GRADE_PRIMARY in value:
                gradeCriteria ^= REQ_CRITERIA.VEHICLE.FAVORITE
            criteria |= gradeCriteria

    return criteria


def buildPopoverTankKeySortCriteria(field):
    if field == VehicleSortColumn.TIER.value:
        return REQ_CRITERIA.CUSTOM(lambda item: item.level)
    if field == VehicleSortColumn.NAME.value:
        return REQ_CRITERIA.CUSTOM(lambda item: item.searchableUserName)
    if field == VehicleSortColumn.TYPE.value:
        criteria = REQ_CRITERIA.CUSTOM(lambda item: VEHICLE_TYPES_ORDER_INDICES[item.type])
        return criteria | REQ_CRITERIA.CUSTOM(lambda item: item.isPremium)


def getRentCriteria():
    return REQ_CRITERIA.CUSTOM(lambda item: item.isRented and not item.isWotPlus)


def getSecretWithoutRentCriteria():
    return REQ_CRITERIA.CUSTOM(lambda item: item.isSecret and not item.isRented)


def getPremiumWithoutRentCriteria():
    return REQ_CRITERIA.CUSTOM(lambda item: item.isPremium and not item.isRented)


def getDocGroupValues(tankman, config, listGetter, valueGetter, sortNeeded=True):
    result = []
    isPremium = tankman.descriptor.isPremium
    tankmanGid = tankman.descriptor.gid
    for gIdx, group in config.getGroups(isPremium).iteritems():
        if not group.notInShop and tankmanGid == gIdx:
            for dIdx in listGetter(group):
                result.append(DocumentRecord(dIdx, gIdx, valueGetter(dIdx)))

    if sortNeeded:
        result = sorted(result, key=lambda sortField: sortField.value, cmp=lambda a, b: strcmp(unicode(a), unicode(b)))
    return result


def jsonArgsConverter(fields=()):
    from functools import wraps
    from json import loads

    def inner(func):

        @wraps(func)
        def wrapper(self, jsonData, *args, **kwargs):
            newArgs = tuple(((loads(data) if isinstance(data, (str, unicode)) else data) for data in (jsonData.get(field) for field in fields if field))) + args
            return func(self, *newArgs, **kwargs)

        return wrapper

    return inner


ALT_VOICES_PREVIEW = itertools.cycle(('vo_enemy_hp_damaged_by_projectile_by_player', 'vo_enemy_fire_started_by_player', 'vo_enemy_killed_by_player'))

def playRecruitVoiceover(voiceoverParams):
    SoundGroups.g_instance.soundModes.setMode(voiceoverParams.languageMode)
    sound = SoundGroups.g_instance.getSound2D(next(ALT_VOICES_PREVIEW))
    sound.play()
    return sound


def discountPercent(value, defaultValue):
    return int(100 * round(1 - float(value) / defaultValue, 2))
