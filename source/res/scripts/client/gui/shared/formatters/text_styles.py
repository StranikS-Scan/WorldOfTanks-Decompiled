# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/formatters/text_styles.py
import types
from helpers import i18n
from gui import makeHtmlString
from gui.shared.money import Currency
__all__ = ('standard',
 'main',
 'neutral',
 'stats',
 'statInfo',
 'statusAlert',
 'middleTitle',
 'highTitle',
 'disabled',
 'promoTitle',
 'promoSubTitle',
 'alert',
 'success',
 'error',
 'warning',
 'critical',
 'expText',
 'expTextBig',
 Currency.GOLD,
 Currency.CREDITS,
 Currency.CRYSTAL,
 'defRes',
 'counter',
 'titleFont',
 'tutorial',
 'playerOnline',
 'getRawStyles',
 'getStyles',
 'concatStylesToSingleLine',
 'concatStylesToMultiLine',
 'superPromoTitle',
 'highlightText',
 'unavailable',
 'missionStatusAvailable')

def _getStyle(style, ctx=None):
    if ctx is None:
        ctx = {}
    return makeHtmlString('html_templates:lobby/textStyle', style, ctx)


def _formatText(style, text=''):
    if type(text) in types.StringTypes and i18n.isValidKey(text):
        text = i18n.makeString(text)
    return _getStyle(style, {'message': text})


def standard(text):
    return _formatText('standardText', text)


def locked(text):
    return _formatText('lockedText', text)


def main(text):
    return _formatText('mainText', text)


def neutral(text):
    return _formatText('neutralText', text)


def goodPing(text):
    return _formatText('goodPingText', text)


def standartPing(text):
    return _formatText('standartPingText', text)


def stats(text):
    return _formatText('statsText', text)


def statInfo(text):
    return _formatText('statusInfoText', text)


def statusAlert(text):
    return _formatText('statusAlert', text)


def middleTitle(text):
    return _formatText('middleTitle', text)


def middleTitleLocked(text):
    return _formatText('middleTitleLocked', text)


def middleBonusTitle(text):
    return _formatText('middleBonusTitle', text)


def highTitle(text):
    return _formatText('highTitle', text)


def goldTextBig(text):
    return _formatText('goldTextBig', text)


def creditsTextBig(text):
    return _formatText('creditsTextBig', text)


def expTextBig(text):
    return _formatText('expTextBig', text)


def errCurrencyTextBig(text):
    return _formatText('errCurrencyTextBig', text)


def disabled(text):
    return _formatText('disabledText', text)


def promoTitle(text):
    return _formatText('promoTitle', text)


def superPromoTitle(text):
    return _formatText('superPromoTitle', text)


def bonusLocalText(text):
    return _formatText('bonusLocalText', text)


def bonusLocalInfoTipText(text):
    return _formatText('bonusLocalInfoTipText', text)


def bonusAppliedText(text):
    return _formatText('bonusAppliedText', text)


def bonusPreviewText(text):
    return _formatText('bonusPreviewText', text)


def promoSubTitle(text):
    return _formatText('promoSubTitle', text)


def alert(text):
    return _formatText('alertText', text)


def success(text):
    return _formatText('successText', text)


def error(text):
    return _formatText('errorText', text)


def warning(text):
    return _formatText('statusWarningText', text)


def critical(text):
    return _formatText('statusCriticalText', text)


def expText(text):
    return _formatText('expText', text)


def gold(text):
    return _formatText('goldText', text)


def goldSmall(text):
    return _formatText('goldTextSmall', text)


def credits(text):
    return _formatText('creditsText', text)


def creditsSmall(text):
    return _formatText('creditsTextSmall', text)


def crystal(text):
    return _formatText('crystalText', text)


def defRes(text):
    return _formatText('defresText', text)


def counter(text):
    return _formatText('counterText', text)


def counterLabelText(text):
    return _formatText('counterLabelText', text)


def titleFont(text):
    return _formatText('titleFont', text)


def tutorial(text):
    return _formatText('tutorialText', text)


def playerOnline(text):
    return _formatText('playerOnline', text)


def hightlight(text):
    return _formatText('highlightText', text)


def alignText(text, align):
    return _getStyle('alignText', {'message': text,
     'align': align})


def alignStandartText(text, align):
    return alignText(standard(text), align)


def vehicleStatusSimpleText(text):
    return _formatText('vehicleStatusSimpleText', text)


def vehicleStatusInfoText(text):
    return _formatText('vehicleStatusInfoText', text)


def vehicleStatusCriticalText(text):
    return _formatText('vehicleStatusCriticalText', text)


def vehicleName(text):
    return _formatText('vehicleName', text)


def premiumVehicleName(text):
    return _formatText('premiumVehicleName', text)


def highlightText(text):
    return _formatText('highlightText', text)


def unavailable(text):
    return _formatText('missionStatusUnavailable', text)


def missionStatusAvailable(text):
    return _formatText('missionStatusAvailable', text)


def getRawStyles(names):
    return dict(map(lambda name: (name, _getStyle(name)), names))


def getStyles(names):
    return dict(map(lambda name: (name, _formatText(name)), names))


def _processStyle(style):
    if hasattr(style, '__iter__'):
        if not style:
            raise ValueError('Empty sequence')
        return _formatText(*style[:1])
    else:
        return _formatText(style)


def concatStylesToSingleLine(*styles):
    return ''.join(map(_processStyle, styles))


def concatStylesToMultiLine(*styles):
    return '\n'.join(map(_processStyle, styles))


def concatStylesWithSpace(*styles):
    return ' '.join(map(_processStyle, styles))


class _StylesBuilder(object):

    def __init__(self, delimiter=''):
        super(_StylesBuilder, self).__init__()
        self.__chunks = []
        self.__delimiter = delimiter

    def addStyledText(self, style, text=''):
        self.__chunks.append((style, text))
        return self

    def render(self):
        result = []
        for style, text in self.__chunks:
            if isinstance(style, types.FunctionType):
                result.append(style(text))
            result.append(_formatText(style, text))

        return self.__delimiter.join(result)


def builder(delimiter=''):
    return _StylesBuilder(delimiter)
