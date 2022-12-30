# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/awards/event_dispatcher.py
import gui.awards.special_achievement_awards as specialAwards
from gui.shared.event_dispatcher import showAwardWindow
from gui.impl.lobby.reward_window import DynamicRewardWindow

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


def showTelecomAward(vehicleDesrs, bundleID, hasCrew, hasBrotherhood):
    showAwardWindow(specialAwards.TelecomAward(vehicleDesrs, bundleID, hasCrew, hasBrotherhood))


def showRecruiterAward():
    showAwardWindow(specialAwards.RecruiterAward())


def showDynamicAward(eventName, bonuses):
    window = DynamicRewardWindow({'eventName': eventName,
     'bonuses': bonuses})
    window.load()


def showVehicleCollectorAward(nationID):
    showAwardWindow(specialAwards.VehicleCollectorAward(nationID))


def showVehicleCollectorOfEverythingAward(*args):
    showAwardWindow(specialAwards.VehicleCollectorOfEverythingAward())
