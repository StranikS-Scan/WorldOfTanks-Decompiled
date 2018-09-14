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


def alert():
    return _getIcon('alert')


def arrow():
    return _getIcon('arrowButton')
