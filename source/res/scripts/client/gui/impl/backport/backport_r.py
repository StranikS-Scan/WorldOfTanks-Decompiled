# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/backport/backport_r.py
import logging
import typing
from frameworks import wulf
from gui.impl.gen import R
if typing.TYPE_CHECKING:
    from gui.impl.gen_utils import DynAccessor
_logger = logging.getLogger(__name__)

def textRes(key):
    path = key.replace('#', '').replace(':', '/').split('/')
    r = R.strings
    for p in path:
        r = r.dyn(p)

    return r


def text(resId, *args, **kwargs):
    if resId <= 0:
        _logger.warning('Invalid resId')
        return ''
    if args:
        try:
            translatedText = wulf.getTranslatedTextByResId(resId, args)
        except (TypeError, ValueError):
            _logger.warning("Arguments do not match string with resId '%r': %r", resId, args)
            return ''

    elif kwargs:
        try:
            translatedText = wulf.getTranslatedTextByResId(resId, kwargs)
        except (TypeError, ValueError):
            _logger.warning("Arguments do not match string with resId '%r': %r", resId, kwargs)
            return ''

    else:
        translatedText = wulf.getTranslatedTextByResId(resId)
    return '' if translatedText == '?empty?' else translatedText


def msgid(resId):
    return wulf.getTranslatedKey(resId)


def image(resId):
    return wulf.getImagePath(resId)


def sound(resId):
    return wulf.getSoundEffectId(resId)


def layout(resId):
    return wulf.getLayoutPath(resId)
