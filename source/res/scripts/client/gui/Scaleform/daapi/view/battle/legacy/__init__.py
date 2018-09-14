# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/legacy/__init__.py
from account_helpers.settings_core import g_settingsCore
AMMO_ICON_PATH = '../maps/icons/ammopanel/battle_ammo/%s'
NO_AMMO_ICON_PATH = '../maps/icons/ammopanel/battle_ammo/NO_%s'
COMMAND_AMMO_CHOICE_MASK = 'CMD_AMMO_CHOICE_{0:d}'
FALLOUT_SCORE_PANEL = '_level0.fragCorrelationBar'
DAMAGE_PANEL_PATH = '_level0.damagePanel'
TANK_INDICATOR_PANEL_PATH = '_level0.damagePanel.tankIndicator'

def findHTMLFormat(item, ctx, csManager, panels):
    if ctx.isPlayerSelected(item):
        return getHTMLString('selected' if item.isReady() else 'selected_dead', csManager)
    else:
        isAliveAndIntoArena = item.isAlive() and item.isReady()
        if ctx.isSquadMan(item):
            return getHTMLString('squad' if isAliveAndIntoArena else 'squad_dead', csManager)
        if ctx.isTeamKiller(item):
            return getHTMLString('teamkiller' if isAliveAndIntoArena else 'teamkiller_dead', csManager)
        normalId = 'normal_white' if panels else 'normal'
        return getHTMLString(normalId if isAliveAndIntoArena else 'normal_dead', csManager)


def getColorValue(schemeName, csManager):
    isColorBlind = g_settingsCore.getSetting('isColorBlind')
    rgba = csManager.getSubScheme(schemeName, isColorBlind)['rgba']
    return (int(rgba[0]) << 16) + (int(rgba[1]) << 8) + (int(rgba[2]) << 0)


def getHTMLString(colorScheme, csManager):
    color = getColorValue(colorScheme, csManager)
    if color:
        result = "<font color='#{0:06x}'>%s</font><br/>".format(color)
    else:
        result = '<font>%s</font><br/>'
    return result
