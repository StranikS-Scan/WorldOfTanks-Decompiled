# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/awards/event_dispatcher.py
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
import gui.awards.special_achievement_awards as specialAwards
from gui.shared.event_dispatcher import showAwardWindow, showModalAwardWindow

def showResearchAward(vehiclesCount, messageNumber):
    showAwardWindow(specialAwards.ResearchAward(vehiclesCount, messageNumber))


def showVictoryAward(victoriesCount, messageNumber):
    showAwardWindow(specialAwards.VictoryAward(victoriesCount, messageNumber))


def showBattleAward(battlesCount, messageNumber):
    showAwardWindow(specialAwards.BattleAward(battlesCount, messageNumber))


def showPveBattleAward(battlesCount, messageNumber):
    showAwardWindow(specialAwards.PvEBattleAward(battlesCount, messageNumber))


def showBoosterAward(booster):
    showAwardWindow(specialAwards.BoosterAward(booster))


def showClanJoinAward(clanAbbrev, clanName, clanDbID):
    showAwardWindow(specialAwards.ClanJoinAward(clanAbbrev, clanName, clanDbID))


def showTelecomAward(vehicleDesrs, hasCrew, hasBrotherhood):
    showAwardWindow(specialAwards.TelecomAward(vehicleDesrs, hasCrew, hasBrotherhood))


def showRecruiterAward():
    showAwardWindow(specialAwards.RecruiterAward())


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def showCrewSkinAward(lobbyContext=None):
    if lobbyContext.getServerSettings().isCrewSkinsEnabled():
        showModalAwardWindow(specialAwards.CrewSkinAward())
