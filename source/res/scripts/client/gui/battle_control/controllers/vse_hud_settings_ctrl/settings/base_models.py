# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/vse_hud_settings_ctrl/settings/base_models.py
import typing
from helpers import i18n
from pve_battle_hud import getPveHudLogger
_logger = getPveHudLogger()

def validateTemplateKey(func):

    def wrapper(self, templateKey, *args, **kwargs):
        if templateKey is None:
            result = ''
        elif i18n.isValidKey(templateKey):
            result = func(self, templateKey, *args, **kwargs)
            if result.startswith('#'):
                _logger.error('Text for key=%s not found.', templateKey)
        else:
            result = templateKey.replace('\\n', '\n')
            if args:
                validParams = _normalizeParams(templateKey, args[0])
                result = result % tuple(validParams)
        return result

    return wrapper


def _normalizeParams(text, params):
    places = text.count('%')
    parameters = len(params)
    emptyPlaces = places - parameters
    if emptyPlaces > 0:
        _logger.error('Not enough params. text=%s, params=%s', text, params)
        params = list(params) + [''] * emptyPlaces
    elif emptyPlaces < 0:
        _logger.error('Too much params for template. text=%s, params=%s', text, params)
        params = params[:emptyPlaces]
    return params


class BaseClientModel(object):
    pass


class TextClientModel(BaseClientModel):

    @validateTemplateKey
    def _getText(self, templateKey):
        return i18n.makeString(templateKey)

    @validateTemplateKey
    def _getPluralText(self, templateKey, params):
        validParams = _normalizeParams(i18n.makeString(templateKey), params)
        pluralTemplate = templateKey.replace(':', ':plural/')
        pluralNumber = validParams[0] if validParams else 0
        return i18n.makePluralString(templateKey, pluralTemplate, pluralNumber, *validParams)
