# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/gui/impl/battle/__init__.py
from grinch_common.grinch_constants import Teams
from grinch.gui.impl.gen.view_models.views.battle.grinch_marker_model import MarkerTypeEnum
from grinch.gui.impl.gen.view_models.views.battle.team_score_model import TeamColorEnum

def getTeamColorModelData(team):
    if team == Teams.CYAN:
        return TeamColorEnum.BLUE
    if team == Teams.YELL:
        return TeamColorEnum.YELLOW
    return TeamColorEnum.MAGENTA if team == Teams.MGNT else TeamColorEnum.NEUTRAL


def getMarkerTypeModelData(team):
    if team == Teams.CYAN:
        return MarkerTypeEnum.BLUE
    if team == Teams.YELL:
        return MarkerTypeEnum.YELLOW
    if team == Teams.MGNT:
        return MarkerTypeEnum.MAGENTA
    return MarkerTypeEnum.CENTRAL if team == Teams.BOTS else MarkerTypeEnum.NONE
