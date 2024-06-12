# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/backport/backport_r.py
import typing
import logging
from constants import IS_DEVELOPMENT
from frameworks import wulf
_logger = logging.getLogger(__name__)

def text(resId, *args, **kwargs):
    if resId <= 0:
        _logger.warning('Invalid resId')
        if IS_DEVELOPMENT:
            import traceback
            traceback.print_stack(limit=2)
        return u''
    if args:
        try:
            return wulf.getTranslatedTextByResId(resId, args)
        except (TypeError, ValueError):
            _logger.warning("Arguments do not match string with resId '%r': %r", resId, args)
            return u''

    elif kwargs:
        try:
            return wulf.getTranslatedTextByResId(resId, kwargs)
        except (TypeError, ValueError):
            _logger.warning("Arguments do not match string with resId '%r': %r", resId, kwargs)
            return u''

    return wulf.getTranslatedTextByResId(resId)


def ntext(resId, n, *args, **kwargs):
    if resId <= 0:
        _logger.warning('Invalid resId')
        if IS_DEVELOPMENT:
            import traceback
            traceback.print_stack(limit=2)
        return u''
    if args:
        try:
            return wulf.getTranslatedPluralTextByResId(resId, n, args)
        except (TypeError, ValueError):
            _logger.warning("Arguments do not match string with resId '%r': %r", resId, args)
            return u''

    elif kwargs:
        try:
            return wulf.getTranslatedPluralTextByResId(resId, n, kwargs)
        except (TypeError, ValueError):
            _logger.warning("Arguments do not match string with resId '%r': %r", resId, kwargs)
            return u''

    return wulf.getTranslatedPluralTextByResId(resId, n)


def msgid(resId):
    return wulf.getTranslatedKey(resId)


def image(resId):
    return wulf.getImagePath(resId)


def sound(resId):
    return wulf.getSoundEffectId(resId)


def layout(resId):
    return wulf.getLayoutPath(resId)
