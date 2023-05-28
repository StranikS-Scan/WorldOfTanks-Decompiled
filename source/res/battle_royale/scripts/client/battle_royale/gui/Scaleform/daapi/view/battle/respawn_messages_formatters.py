# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/battle/respawn_messages_formatters.py
from gui.Scaleform.genConsts.BATTLE_ROYAL_CONSTS import BATTLE_ROYAL_CONSTS
from gui.impl import backport
from gui.impl.gen import R

def formatRespawnActivatedMessage(time, delay=0):
    return {'time': time,
     'delay': delay,
     'quickHide': False,
     'title': backport.text(R.strings.battle_royale.battle.respawnMessagePanel.respawnActivated.title()),
     'description': backport.text(R.strings.battle_royale.battle.respawnMessagePanel.respawnActivated.description()),
     'messageLinkage': BATTLE_ROYAL_CONSTS.MESSAGE_TIMER_LINKAGE}


def formatRespawnFinishedMessage(time, delay=0):
    return {'time': time,
     'delay': delay,
     'quickHide': False,
     'title': backport.text(R.strings.battle_royale.battle.respawnMessagePanel.respawned.title()),
     'description': backport.text(R.strings.battle_royale.battle.respawnMessagePanel.respawned.description()),
     'messageLinkage': BATTLE_ROYAL_CONSTS.MESSAGE_RESPAWN_NO_ICON_LINKAGE}


def formatRespawnNotAvailableMessage(time, delay=0):
    return {'time': time,
     'delay': delay,
     'quickHide': False,
     'title': backport.text(R.strings.battle_royale.battle.respawnMessagePanel.respawnNotAvailable.title()),
     'description': backport.text(R.strings.battle_royale.battle.respawnMessagePanel.respawnNotAvailable.description()),
     'messageLinkage': BATTLE_ROYAL_CONSTS.MESSAGE_RESPAWN_NOT_AVAILABLE_LINKAGE}


def formatRespawnNotAvailableSoonMessage(time, delay=0):
    return {'time': time,
     'delay': delay,
     'quickHide': False,
     'title': backport.text(R.strings.battle_royale.battle.respawnMessagePanel.respawnNotAvailableSoon.title()),
     'messageLinkage': BATTLE_ROYAL_CONSTS.MESSAGE_RESPAWN_NO_ICON_LINKAGE}


def formatRespawnActivatedSquadMessage(time, delay=0):
    return {'time': time,
     'delay': delay,
     'quickHide': False,
     'title': backport.text(R.strings.battle_royale.battle.respawnMessagePanel.respawnActivatedSquad.title()),
     'messageLinkage': BATTLE_ROYAL_CONSTS.MESSAGE_TIMER_LINKAGE}


def formatAllyInBattleMessage(time, delay=0):
    return {'time': time,
     'delay': delay,
     'quickHide': False,
     'title': backport.text(R.strings.battle_royale.battle.respawnMessagePanel.squad.inBattle.title()),
     'description': backport.text(R.strings.battle_royale.battle.respawnMessagePanel.squad.inBattle.description()),
     'messageLinkage': BATTLE_ROYAL_CONSTS.MESSAGE_RESPAWN_AVAILABLE_LINKAGE}


def formatPickUpSphereMessage(time, delay=0):
    return {'time': time,
     'delay': delay,
     'quickHide': False,
     'title': backport.text(R.strings.battle_royale.battle.respawnMessagePanel.squad.pickUp.title()),
     'description': backport.text(R.strings.battle_royale.battle.respawnMessagePanel.squad.pickUp.description()),
     'messageLinkage': BATTLE_ROYAL_CONSTS.MESSAGE_RESPAWN_NO_ICON_LINKAGE}


def formatStayInCoverMessage(time, delay=0):
    return {'time': time,
     'delay': delay,
     'quickHide': False,
     'title': backport.text(R.strings.battle_royale.battle.respawnMessagePanel.squad.stayInCover.title()),
     'description': backport.text(R.strings.battle_royale.battle.respawnMessagePanel.squad.stayInCover.description()),
     'messageLinkage': BATTLE_ROYAL_CONSTS.MESSAGE_TIMER_LINKAGE}


def formatAllyRespawnedMessage(time, delay=0):
    return {'time': time,
     'delay': delay,
     'quickHide': False,
     'title': backport.text(R.strings.battle_royale.battle.respawnMessagePanel.squad.squadmanRespawned.title()),
     'description': backport.text(R.strings.battle_royale.battle.respawnMessagePanel.squad.squadmanRespawned.description()),
     'messageLinkage': BATTLE_ROYAL_CONSTS.MESSAGE_RESPAWN_NO_ICON_LINKAGE}


def formatAllyRespawnInProgressMessage(time, delay=0):
    return {'time': time,
     'delay': delay,
     'quickHide': False,
     'title': backport.text(R.strings.battle_royale.battle.respawnMessagePanel.squad.respawning.title()),
     'messageLinkage': BATTLE_ROYAL_CONSTS.MESSAGE_TIMER_LINKAGE}
