# Embedded file name: scripts/client/gui/awards/event_dispatcher.py
import gui.awards.special_achievement_awards as specialAwards
from gui.shared.event_dispatcher import showAwardWindow, showPremiumCongratulationWindow

def showResearchAward(vehiclesCount, messageNumber):
    showAwardWindow(specialAwards.ResearchAward(vehiclesCount, messageNumber))


def showVictoryAward(victoriesCount, messageNumber):
    showAwardWindow(specialAwards.VictoryAward(victoriesCount, messageNumber))


def showBattleAward(battlesCount, messageNumber):
    showAwardWindow(specialAwards.BattleAward(battlesCount, messageNumber))


def showPveBattleAward(battlesCount, messageNumber):
    showAwardWindow(specialAwards.PvEBattleAward(battlesCount, messageNumber))


def showPremiumDiscountAward(researchLvl, premiumPacket, discount):
    showPremiumCongratulationWindow(specialAwards.PremiumDiscountAward(researchLvl, premiumPacket, discount))


def showBoosterAward(booster):
    showAwardWindow(specialAwards.BoosterAward(booster))


def showFalloutAward(lvls, isRequiredVehicle = False):
    showAwardWindow(specialAwards.FalloutAwardWindow(lvls, isRequiredVehicle))
