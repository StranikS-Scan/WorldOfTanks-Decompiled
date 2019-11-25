# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/backport/backport_r.py
import logging
from frameworks import wulf
_logger = logging.getLogger(__name__)

def text(resId, *args, **kwargs):
    if resId <= 0:
        _logger.warning('Invalid resId')
        return ''
    if args:
        try:
            return wulf.getTranslatedTextByResId(resId, args)
        except (TypeError, ValueError):
            _logger.warning("Arguments do not match string with resId '%r': %r", resId, args)
            return ''

    elif kwargs:
        try:
            return wulf.getTranslatedTextByResId(resId, kwargs)
        except (TypeError, ValueError):
            _logger.warning("Arguments do not match string with resId '%r': %r", resId, kwargs)
            return ''

    return wulf.getTranslatedTextByResId(resId)


def msgid(resId):
    return wulf.getTranslatedKey(resId)


def image(resId):
    return wulf.getImagePath(resId)


def sound(resId):
    return wulf.getSoundEffectId(resId)


def layout(resId):
    return wulf.getLayoutPath(resId)
