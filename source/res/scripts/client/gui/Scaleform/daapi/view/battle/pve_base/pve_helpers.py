# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/pve_base/pve_helpers.py
import typing
from pve_battle_hud import getPveHudLogger
_logger = getPveHudLogger()

def generateText(template, params):
    places = template.count('%')
    parameters = len(params)
    emptyPlaces = places - parameters
    if emptyPlaces > 0:
        _logger.error('Not enough params. template=%s, params=%s', template, params)
        params = list(params) + [''] * emptyPlaces
    elif emptyPlaces < 0:
        _logger.error('Too much params for template. template=%s, params=%s', template, params)
        params = params[:emptyPlaces]
    return template % tuple(params)
