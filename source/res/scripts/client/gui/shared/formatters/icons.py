# Embedded file name: scripts/client/gui/shared/formatters/icons.py
from gui import makeHtmlString
from gui.shared.utils.functions import getAbsoluteUrl
__all__ = ('noSeason', 'swords', 'alert', 'arrow', 'xp', 'credits', 'notAvailable', 'notAvailableRed', 'checkmark', 'info', 'premiumIgrBig', 'premiumIgrSmall', 'freeXP', 'gold', 'nut', 'clock', 'makeImageTag')
_IMG_TAG_TPL = "<img src='{0}' width='{1}' height='{2}' vspace='{3}' hspace='{4}'/>"

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


def notAvailable():
    return _getIcon('notAvailable')


def notAvailableRed():
    return _getIcon('notAvailableRed')


def checkmark():
    return _getIcon('checkmark')


def envelop():
    return _getIcon('envelope')


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


def nutStat():
    return _getIcon('nutStat')


def clock():
    return _getIcon('clock')


def quest():
    return _getIcon('quest')


def makeImageTag(source, width = 16, height = 16, vSpace = -4, hSpace = 0):
    return _IMG_TAG_TPL.format(getAbsoluteUrl(source), width, height, vSpace, hSpace)
