# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/formatters/icons.py
from gui import makeHtmlString
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.money import Currency
from gui.shared.utils.functions import getAbsoluteUrl
from gui.Scaleform.genConsts.COMPONENTS import COMPONENTS
__all__ = ('noSeason', 'swords', 'alert', 'arrow', 'xp', 'notAvailable', 'notAvailableRed', 'checkmark', 'info', 'premiumIgrBig', 'premiumIgrSmall', 'freeXP', 'nut', 'clock', 'makeImageTag', 'getRoleIcon') + Currency.ALL
_IMG_TAG_TPL = "<img src='{0}' width='{1}' height='{2}' vspace='{3}' hspace='{4}'/>"

def _getIcon(icon, width=None, height=None, vspace=None, hspace=None):
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


def swords(vspace=-4):
    return _getIcon('swords', vspace=vspace)


def alert(vspace=-4):
    return _getIcon('alert', vspace=vspace)


def alertBig(vspace=-6):
    return _getIcon('alertBig', vspace=vspace)


def arrow(vspace=-5):
    return _getIcon('arrowButton', vspace=vspace)


def attention(vspace=-3):
    return _getIcon('attention', vspace=vspace)


def xp():
    return _getIcon('xp')


def credits():
    return _getIcon(Currency.CREDITS)


def creditsBig():
    return _getIcon('creditsBig')


def creditsExtraBig():
    return _getIcon('creditsExtraBig')


def notAvailable():
    return _getIcon('notAvailable')


def notAvailableRed():
    return _getIcon('notAvailableRed')


def checkmark(vspace=-4):
    return _getIcon('checkmark', vspace=vspace)


def check(vspace=-6, hspace=-6):
    return _getIcon('check', vspace=vspace, hspace=hspace)


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


def freeXPExtraBig():
    return _getIcon('freeXPExtraBig')


def xpCost():
    return _getIcon('xpCost')


def xpCostBig():
    return _getIcon('xpCostBig')


def gold():
    return _getIcon(Currency.GOLD)


def goldBig():
    return _getIcon('goldBig')


def goldExtraBig():
    return _getIcon('goldExtraBig')


def crystal():
    return _getIcon(Currency.CRYSTAL)


def crystalBig():
    return _getIcon('crystalBig')


def crystalExtraBig():
    return _getIcon('crystalExtraBig')


def eventCoin():
    return _getIcon(Currency.EVENT_COIN)


def eventCoinBig():
    return _getIcon('eventCoinBig')


def bpcoin():
    return _getIcon(Currency.BPCOIN)


def bpcoinBig():
    return _getIcon('bpcoinBig')


def demountKit():
    return _getIcon('demountKit')


def nut():
    return _getIcon('nut')


def nutStat():
    return _getIcon('nutStat')


def clock():
    return _getIcon('clock')


def clockGold():
    return _getIcon('clockGold')


def quest():
    return _getIcon('quest')


def serverAlert():
    return _getIcon('serverAlert')


def markerBlocked(vspace=-2):
    return _getIcon('markerBlocked', vspace=vspace)


def awardList():
    return _getIcon('awardList')


def inProgress(vspace=-2):
    return _getIcon('inProgress', vspace=vspace)


def doubleCheckmark(vspace=0):
    return _getIcon('doubleCheckmark', vspace=vspace)


def actionBlue():
    return _getIcon('actionBlueBg')


def actionRed():
    return _getIcon('actionBlueBg')


def starYellow(vspace=-4):
    return _getIcon('starYellow', vspace=vspace)


def webLink():
    return _getIcon('webLink')


def makeImageTag(source, width=16, height=16, vSpace=-4, hSpace=0):
    return _IMG_TAG_TPL.format(getAbsoluteUrl(source), width, height, vSpace, hSpace)


def getRoleIcon(role, vSpace=-6, width=24, height=24):
    if role == 'role_' + COMPONENTS.SPG:
        return ''
    source = backport.image(R.images.gui.maps.icons.roleExp.roles.c_24x24.dyn(role)())
    return makeImageTag(source, width=width, height=height, vSpace=vSpace)


def lightning(vSpace=-4):
    source = backport.image(R.images.gui.maps.icons.library.lightning())
    return makeImageTag(source, width=10, height=16, vSpace=vSpace)


def serverBlockerIcon():
    source = backport.image(R.images.gui.maps.icons.library.blocker())
    return makeImageTag(source, width=14, height=14, vSpace=-3)
