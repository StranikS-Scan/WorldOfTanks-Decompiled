# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/client_worlds_helpers.py
import CGF
import enum
import BattleReplay
from cgf_script.managers_registrator import autoregister
from constants import IS_UE_EDITOR
from helpers import isPlayerAccount, isPlayerAvatar

class ClientWorld(enum.IntEnum):
    NONE = 0
    BATTLE = 1
    HANGAR = 2
    EDITOR = 4
    AllWorlds = BATTLE | HANGAR | EDITOR


def getClientWorld():
    if IS_UE_EDITOR:
        clientWorld = ClientWorld.EDITOR
    elif isPlayerAccount():
        clientWorld = ClientWorld.HANGAR
    elif isPlayerAvatar() or BattleReplay.isPlaying() or BattleReplay.isServerSideReplay():
        clientWorld = ClientWorld.BATTLE
    else:
        clientWorld = ClientWorld.NONE
    return clientWorld


def clientWorldsPredicate(clientWorlds):

    def predicate(_):
        return bool(getClientWorld() & clientWorlds)

    return predicate


def clientWorldsManager(clientWorlds):
    domain = CGF.DomainOption.DomainClient
    if ClientWorld.EDITOR & clientWorlds:
        domain |= CGF.DomainOption.DomainEditor
    return autoregister(presentInAllWorlds=True, creationPredicate=clientWorldsPredicate(clientWorlds), domain=domain)
