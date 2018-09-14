# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/awards/event_dispatcher.py
import gui.awards.special_achievement_awards as specialAwards
from gui.shared.event_dispatcher import showAwardWindow
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS

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


def showFalloutAward(lvls, isRequiredVehicle=False):
    showAwardWindow(specialAwards.FalloutAwardWindow(lvls, isRequiredVehicle))


def showClanJoinAward(clanAbbrev, clanName, clanDbID):
    showAwardWindow(specialAwards.ClanJoinAward(clanAbbrev, clanName, clanDbID))


def showTelecomAward(vehicleDesrs, hasCrew, hasBrotherhood):
    showAwardWindow(specialAwards.TelecomAward(vehicleDesrs, hasCrew, hasBrotherhood))


def showChristmasAward(color, bonuses, christmasController):
    showAwardWindow(specialAwards.ChristmasAward(color, bonuses, christmasController))


def showChristmasPackAward(color, boxCount, bonuses, christmasController):
    showAwardWindow(specialAwards.ChristmasPackAward(color, boxCount, bonuses, christmasController))


def showLvlUpChristmasAward(lvl, christmasController):
    showAwardWindow(specialAwards.ChristmasLvlUpAward(lvl, christmasController), viewAlias=VIEW_ALIAS.CHRISTMAS_LVL_UP_AWARD_WINDOW)
