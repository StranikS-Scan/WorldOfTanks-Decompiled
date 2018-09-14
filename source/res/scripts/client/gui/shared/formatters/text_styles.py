# Embedded file name: scripts/client/gui/shared/formatters/text_styles.py
import types
from helpers import i18n
from gui import makeHtmlString
__all__ = ('standard', 'main', 'neutral', 'stats', 'statInfo', 'middleTitle', 'highTitle', 'disabled', 'promoTitle', 'promoSubTitle', 'alert', 'success', 'error', 'warning', 'critical', 'expText', 'gold', 'credits', 'defRes', 'counter', 'titleFont', 'tutorial', 'playerOnline', 'getRawStyles', 'getStyles', 'concatStylesToSingleLine', 'concatStylesToMultiLine')

def _getStyle(style, ctx = None):
    if ctx is None:
        ctx = {}
    return makeHtmlString('html_templates:lobby/textStyle', style, ctx)


def _formatText(style, text = ''):
    if type(text) in types.StringTypes and i18n.isValidKey(text):
        text = i18n.makeString(text)
    return _getStyle(style, {'message': text})


def standard(text):
    return _formatText('standardText', text)


def main(text):
    return _formatText('mainText', text)


def neutral(text):
    return _formatText('neutralText', text)


def stats(text):
    return _formatText('statsText', text)


def statInfo(text):
    return _formatText('statusInfoText', text)


def middleTitle(text):
    return _formatText('middleTitle', text)


def highTitle(text):
    return _formatText('highTitle', text)


def goldTextBig(text):
    return _formatText('goldTextBig', text)


def creditsTextBig(text):
    return _formatText('creditsTextBig', text)


def errCurrencyTextBig(text):
    return _formatText('errCurrencyTextBig', text)


def disabled(text):
    return _formatText('disabledText', text)


def promoTitle(text):
    return _formatText('promoTitle', text)


def bonusLocalText(text):
    return _formatText('bonusLocalText', text)


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


def credits(text):
    return _formatText('creditsText', text)


def defRes(text):
    return _formatText('defresText', text)


def counter(text):
    return _formatText('counterText', text)


def titleFont(text):
    return _formatText('titleFont', text)


def tutorial(text):
    return _formatText('tutorialText', text)


def playerOnline(text):
    return _formatText('playerOnline', text)


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

    def __init__(self, delimiter = ''):
        super(_StylesBuilder, self).__init__()
        self.__chunks = []
        self.__delimiter = delimiter

    def addStyledText(self, style, text = ''):
        self.__chunks.append((style, text))
        return self

    def render(self):
        result = []
        for style, text in self.__chunks:
            if isinstance(style, types.FunctionType):
                result.append(style(text))
            else:
                result.append(_formatText(style, text))

        return self.__delimiter.join(result)


def builder(delimiter = ''):
    return _StylesBuilder(delimiter)
