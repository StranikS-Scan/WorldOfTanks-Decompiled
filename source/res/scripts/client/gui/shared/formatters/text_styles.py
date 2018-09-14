# Embedded file name: scripts/client/gui/shared/formatters/text_styles.py
from helpers import i18n
from gui import makeHtmlString

def _formatText(style, text = ''):
    if i18n.isValidKey(text):
        text = i18n.makeString(text)
    return makeHtmlString('html_templates:lobby/textStyle', style, {'message': text})


def main(text):
    return _formatText('mainText', text)


def neutral(text):
    return _formatText('neutralText', text)


def stats(text):
    return _formatText('statsText', text)


def middleTitle(text):
    return _formatText('middleTitle', text)


def highTitle(text):
    return _formatText('highTitle', text)


def disable(text):
    return _formatText('disabledText', text)
