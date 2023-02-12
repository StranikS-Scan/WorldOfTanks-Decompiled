# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/platoon/platoon_config.py
import logging
from collections import namedtuple
from enum import Enum
from constants import PREBATTLE_TYPE, QUEUE_TYPE
from gui.impl.lobby.platoon.view.platoon_members_view import SquadMembersView, EventMembersView, EpicMembersView, BattleRoyalMembersView, MapboxMembersView, Comp7MembersView
from gui.impl.gen import R
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.impl.lobby.platoon.view.platoon_members_view import MembersWindow
from gui.impl.lobby.platoon.view.platoon_search_view import SearchWindow
from gui.impl.lobby.platoon.view.platoon_selection_view import SelectionWindow
from gui.impl.lobby.platoon.view.platoon_welcome_view import WelcomeView
from gui.impl.lobby.platoon.view.comp7_platoon_welcome_view import Comp7WelcomeView
from gui.shared.utils.requesters import REQ_CRITERIA
from soft_exception import SoftException
_logger = logging.getLogger(__name__)
SquadInfo = namedtuple('SquadInfo', ['platoonState', 'squadManStates', 'commanderIndex'])
Position = namedtuple('Position', ['x', 'y'])
PlatoonLayout = namedtuple('PlatoonLayout', ('layoutID', 'windowClass'))
PrbEntityInfo = namedtuple('PrbEntityInfo', ['queueType', 'prebattleType'])

class EPlatoonLayout(Enum):
    WELCOME = 0
    SEARCH = 1
    MEMBER = 2


DEFAULT_LAYOUTS_KEY = 'default'
ePlatoonLayouts = {EPlatoonLayout.WELCOME: {DEFAULT_LAYOUTS_KEY: PlatoonLayout(R.views.lobby.platoon.PlatoonDropdown(), SelectionWindow)},
 EPlatoonLayout.SEARCH: {DEFAULT_LAYOUTS_KEY: PlatoonLayout(R.views.lobby.platoon.SearchingDropdown(), SearchWindow)},
 EPlatoonLayout.MEMBER: {DEFAULT_LAYOUTS_KEY: PlatoonLayout(R.views.lobby.platoon.MembersWindow(), MembersWindow)}}

def buildCurrentLayouts(prbType=DEFAULT_LAYOUTS_KEY):
    layouts = {}
    for layout, layoutData in ePlatoonLayouts.iteritems():
        layouts[layout] = layoutData[prbType] if prbType in layoutData else layoutData[DEFAULT_LAYOUTS_KEY]

    return layouts


PLATOON_VIEW_BY_PRB_TYPE = {PREBATTLE_TYPE.SQUAD: SquadMembersView,
 PREBATTLE_TYPE.EVENT: EventMembersView,
 PREBATTLE_TYPE.EPIC: EpicMembersView,
 PREBATTLE_TYPE.BATTLE_ROYALE: BattleRoyalMembersView,
 PREBATTLE_TYPE.MAPBOX: MapboxMembersView,
 PREBATTLE_TYPE.COMP7: Comp7MembersView}
QUEUE_TYPE_TO_PREBATTLE_ACTION_NAME = {QUEUE_TYPE.EVENT_BATTLES: PREBATTLE_ACTION_NAME.EVENT_SQUAD,
 QUEUE_TYPE.RANDOMS: PREBATTLE_ACTION_NAME.SQUAD,
 QUEUE_TYPE.EPIC: PREBATTLE_ACTION_NAME.SQUAD,
 QUEUE_TYPE.BATTLE_ROYALE: PREBATTLE_ACTION_NAME.BATTLE_ROYALE_SQUAD,
 QUEUE_TYPE.MAPBOX: PREBATTLE_ACTION_NAME.MAPBOX_SQUAD,
 QUEUE_TYPE.COMP7: PREBATTLE_ACTION_NAME.COMP7_SQUAD}
PRB_TYPE_TO_WELCOME_VIEW_CONTENT_FACTORY = {PREBATTLE_TYPE.SQUAD: WelcomeView,
 PREBATTLE_TYPE.FALLOUT: WelcomeView,
 PREBATTLE_TYPE.EVENT: WelcomeView,
 PREBATTLE_TYPE.EPIC: WelcomeView,
 PREBATTLE_TYPE.BATTLE_ROYALE: WelcomeView,
 PREBATTLE_TYPE.MAPBOX: WelcomeView,
 PREBATTLE_TYPE.COMP7: Comp7WelcomeView}
RANDOM_VEHICLE_CRITERIA = ~(REQ_CRITERIA.VEHICLE.EPIC_BATTLE ^ REQ_CRITERIA.VEHICLE.BATTLE_ROYALE ^ REQ_CRITERIA.VEHICLE.EVENT_BATTLE ^ REQ_CRITERIA.VEHICLE.MAPS_TRAINING)
PREBATTLE_TYPE_TO_VEH_CRITERIA = {PREBATTLE_TYPE.SQUAD: RANDOM_VEHICLE_CRITERIA,
 PREBATTLE_TYPE.EPIC: ~(REQ_CRITERIA.VEHICLE.BATTLE_ROYALE ^ REQ_CRITERIA.VEHICLE.EVENT_BATTLE),
 PREBATTLE_TYPE.BATTLE_ROYALE: REQ_CRITERIA.VEHICLE.BATTLE_ROYALE,
 PREBATTLE_TYPE.BATTLE_ROYALE_TOURNAMENT: REQ_CRITERIA.VEHICLE.BATTLE_ROYALE,
 PREBATTLE_TYPE.EVENT: REQ_CRITERIA.VEHICLE.EVENT_BATTLE,
 PREBATTLE_TYPE.MAPBOX: RANDOM_VEHICLE_CRITERIA,
 PREBATTLE_TYPE.COMP7: RANDOM_VEHICLE_CRITERIA}

def addPlatoonViewByPrbType(prbType, platoonView, personality):
    if prbType in PLATOON_VIEW_BY_PRB_TYPE:
        raise SoftException('PLATOON_VIEW_BY_PRB_TYPE already has pre battle type:{prb}. Personality: {p}'.format(prb=prbType, p=personality))
    PLATOON_VIEW_BY_PRB_TYPE.update({prbType: platoonView})
    msg = 'prbType:{prb} was added to PLATOON_VIEW_BY_PRB_TYPE. Personality: {p}'.format(prb=prbType, p=personality)
    logging.debug(msg)


def addPlatoonWelcomeViewByPrbType(prbType, welcomeView, personality):
    if prbType in PRB_TYPE_TO_WELCOME_VIEW_CONTENT_FACTORY:
        raise SoftException('PRB_TYPE_TO_WELCOME_VIEW_CONTENT_FACTORY already has pre battle type:{prb}. Personality: {p}'.format(prb=prbType, p=personality))
    PRB_TYPE_TO_WELCOME_VIEW_CONTENT_FACTORY.update({prbType: welcomeView})
    msg = 'prbType:{prb} was added to PRB_TYPE_TO_WELCOME_VIEW_CONTENT_FACTORY. Personality: {p}'.format(prb=prbType, p=personality)
    logging.debug(msg)


def addQueueTypeToPrbSquadActionName(queueType, prbSquadActionName, personality):
    if queueType in QUEUE_TYPE_TO_PREBATTLE_ACTION_NAME:
        raise SoftException('QUEUE_TYPE_TO_PREBATTLE_ACTION_NAME already has pre battle type:{qType}. Personality: {p}'.format(qType=queueType, p=personality))
    QUEUE_TYPE_TO_PREBATTLE_ACTION_NAME.update({queueType: prbSquadActionName})
    msg = 'queueType:{qtype} was added to QUEUE_TYPE_TO_PREBATTLE_ACTION_NAME. Personality: {p}'.format(qtype=queueType, p=personality)
    logging.debug(msg)


def addPlatoonLayoutData(prbType, layoutsData, personality):
    for layoutType, data in layoutsData:
        if layoutType not in ePlatoonLayouts:
            raise SoftException('ePlatoonLayouts has not layoutType:{layoutType}. Personality: {p}'.format(layoutType=layoutType, p=personality))
        layoutData = ePlatoonLayouts[layoutType]
        if prbType in layoutData:
            raise SoftException('ePlatoonLayouts already has layoutType:{layoutType} for prbType:{prbType}. Personality: {p}'.format(layoutType=layoutType, prbType=prbType, p=personality))
        layoutData[prbType] = data
        msg = 'prbType:{prbType} was added to ePlatoonLayouts for layoutType:{layoutType}. Personality: {p}'.format(prbType=prbType, layoutType=layoutType, p=personality)
        logging.debug(msg)
