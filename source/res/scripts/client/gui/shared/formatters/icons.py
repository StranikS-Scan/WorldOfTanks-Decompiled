# Embedded file name: scripts/client/gui/shared/formatters/icons.py
from gui import makeHtmlString

def _getIcon(icon, width = None, height = None, vspace = None, hspace = None):
    ctx = {}
    if width is not None:
        ctx['width'] = width
    if height is not None:
        ctx['height'] = height
    if vspace is not None:
        ctx['vspace'] = vspace
    if hspace is not None:
        ctx['hspace'] = hspace
    return makeHtmlString('html_templates:lobby/iconText', icon, ctx)


def noSeason():
    return _getIcon('noSeason')


def swords(vspace = -4):
    return _getIcon('swords', vspace=vspace)


def alert(vspace = -4):
    return _getIcon('alert', vspace=vspace)


def arrow():
    return _getIcon('arrowButton')


def xp():
    return _getIcon('xp')


def credits():
    return _getIcon('credits')


def notAvailableRed():
    return _getIcon('notAvailableRed')


def checkmark():
    return _getIcon('checkmark')


def info():
    return _getIcon('info')


def premiumIgrBig():
    return _getIcon('premiumIgrBig')


def premiumIgrSmall():
    return _getIcon('premiumIgrSmall')


def freeXP():
    return _getIcon('freeXP')


def gold():
    return _getIcon('gold')


def nut():
    return _getIcon('nut')


def clock():
    return _getIcon('clock')
