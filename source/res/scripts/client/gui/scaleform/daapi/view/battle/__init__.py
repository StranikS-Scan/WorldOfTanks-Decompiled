# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/__init__.py
from account_helpers.settings_core import g_settingsCore
from debug_utils import LOG_ERROR
AMMO_ICON_PATH = '../maps/icons/ammopanel/ammo/%s'
NO_AMMO_ICON_PATH = '../maps/icons/ammopanel/ammo/NO_%s'
COMMAND_AMMO_CHOICE_MASK = 'CMD_AMMO_CHOICE_{0:d}'
FALLOUT_SCORE_PANEL = '_level0.fragCorrelationBar'
DAMAGE_PANEL_PATH = '_level0.damagePanel'
TANK_INDICATOR_PANEL_PATH = '_level0.damagePanel.tankIndicator'

def findHTMLFormat(item, ctx, csManager):
    if ctx.isPlayerSelected(item):
        return getHTMLString('selected' if item.isReady() else 'selected_dead', csManager)
    isAliveAndIntoArena = item.isAlive() and item.isReady()
    if ctx.isSquadMan(item):
        return getHTMLString('squad' if isAliveAndIntoArena else 'squad_dead', csManager)
    elif ctx.isTeamKiller(item):
        return getHTMLString('teamkiller' if isAliveAndIntoArena else 'teamkiller_dead', csManager)
    else:
        return getHTMLString('normal' if isAliveAndIntoArena else 'normal_dead', csManager)


def getColorValue(colorScheme, csManager):
    __colorGroup = g_settingsCore.getSetting('isColorBlind')
    scheme = csManager.getScheme(colorScheme)
    makeRGB = csManager._makeRGB
    if __colorGroup in scheme:
        color = makeRGB(scheme[__colorGroup])
    elif csManager.DEFAULT_TAG in scheme:
        color = makeRGB(scheme[csManager.DEFAULT_TAG])
    else:
        LOG_ERROR('Current color scheme not found', scheme, __colorGroup)
        color = 0
    return color


def getHTMLString(colorScheme, csManager):
    color = getColorValue(colorScheme, csManager)
    if color:
        result = "<font color='#{0:06x}'>%s</font><br/>".format(color)
    else:
        result = '<font>%s</font><br/>'
    return result
