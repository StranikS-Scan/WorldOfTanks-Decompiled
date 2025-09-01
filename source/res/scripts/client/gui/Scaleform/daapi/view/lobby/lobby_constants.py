# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/lobby_constants.py
import typing
from constants import ARENA_BONUS_TYPE
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from helpers import dependency
from skeletons.gui.game_control import IPlatoonController
if typing.TYPE_CHECKING:
    from typing import Dict

class USER(object):
    INFO = 'userInfo'
    CLAN_INFO = 'clanInfo'
    SEND_CLAN_INVITE = 'sendClanInvite'
    CREATE_PRIVATE_CHANNEL = 'createPrivateChannel'
    ADD_TO_FRIENDS = 'addToFriends'
    REQUEST_FRIENDSHIP = 'requestFriendship'
    REMOVE_FROM_FRIENDS = 'removeFromFriends'
    ADD_TO_IGNORED = 'addToIgnored'
    REMOVE_FROM_IGNORED = 'removeFromIgnored'
    COPY_TO_CLIPBOARD = 'copyToClipBoard'
    SET_MUTED = 'setMuted'
    UNSET_MUTED = 'unsetMuted'
    CREATE_SQUAD = 'createSquad'
    CREATE_EVENT_SQUAD = 'createEventSquad'
    CREATE_BATTLE_ROYALE_SQUAD = 'createBattleRoyaleSquad'
    INVITE = 'invite'
    VEHICLE_INFO = 'vehicleInfoEx'
    END_REFERRAL_COMPANY = 'endReferralCompany'
    CREATE_MAPBOX_SQUAD = 'createMapboxSquad'


SETTINGS_WINDOWS_MAP = {}
DEFAULT_SETTINGS_ALIAS = VIEW_ALIAS.SETTINGS_WINDOW

def registerSettingsWindow(arenaBonusType, viewAlias):
    SETTINGS_WINDOWS_MAP[arenaBonusType] = viewAlias


def getSettingsWindowAlias():
    platoonController = dependency.instance(IPlatoonController)
    arenaBonusCaps = platoonController.getPrbEntityType()
    return SETTINGS_WINDOWS_MAP.get(arenaBonusCaps, DEFAULT_SETTINGS_ALIAS)
