# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/complex_formatters.py
from gui import makeHtmlString
from gui.shared.utils.functions import stripColorTagDescrTags
from helpers import i18n
_TEXT_FORMAT = "{0[0]}{1}{0[1]}\n<font size='1' > </font>\n"
_TOOLTIP_KIND = ('header', 'body', 'note', 'attention')
_HTML_COMPLEX = 'html_templates:lobby/tooltips_complex'
_BLOCK_TAGS_MAP = {'HEADER': {'INFO': (makeHtmlString(_HTML_COMPLEX, 'header_info_start'), makeHtmlString(_HTML_COMPLEX, 'header_info_end')),
            'WARNING': (makeHtmlString(_HTML_COMPLEX, 'header_warning_start'), makeHtmlString(_HTML_COMPLEX, 'header_warning_end'))},
 'BODY': {'INFO': (makeHtmlString(_HTML_COMPLEX, 'body_info_start'), makeHtmlString(_HTML_COMPLEX, 'body_info_end')),
          'WARNING': (makeHtmlString(_HTML_COMPLEX, 'body_warning_start'), makeHtmlString(_HTML_COMPLEX, 'body_warning_end'))},
 'NOTE': {'INFO': (makeHtmlString(_HTML_COMPLEX, 'note_info_start'), makeHtmlString(_HTML_COMPLEX, 'note_info_end')),
          'WARNING': [makeHtmlString(_HTML_COMPLEX, 'note_warning_start'), makeHtmlString(_HTML_COMPLEX, 'note_warning_end')]},
 'ATTENTION': {'INFO': (makeHtmlString(_HTML_COMPLEX, 'attention_info_start'), makeHtmlString(_HTML_COMPLEX, 'attention_info_end')),
               'WARNING': (makeHtmlString(_HTML_COMPLEX, 'attention_warning_start'), makeHtmlString(_HTML_COMPLEX, 'attention_warning_end'))}}

def _getTags(blockType, formatType):
    blockTag = _BLOCK_TAGS_MAP[blockType]
    return blockTag[formatType] if formatType in blockTag else ('', '')


def _getFormattedText(text, blockType, formatType):
    if formatType is None:
        formatType = 'INFO'
    tags = _getTags(blockType, formatType)
    return _TEXT_FORMAT.format(tags, text)


def _doFormatToolTipFromKey(tooltipID, formatType):
    result = []
    for kind in _TOOLTIP_KIND:
        contentKey = '{}/{}'.format(tooltipID, kind)
        content = i18n.makeString(contentKey)
        subkey = contentKey[1:].split(':', 1)
        if content and subkey and content != subkey[1]:
            result.append(_getFormattedText(content, kind.upper(), formatType))

    return ''.join(result)


def _doFormatToolTipFromText(tooltipID, formatType):
    result = ''
    for tooltipKind in _TOOLTIP_KIND:
        tooltipBlock = tooltipKind.upper()
        tags = {'open': '{' + tooltipBlock + '}',
         'close': '{/' + tooltipBlock + '}'}
        indicies = {'start': tooltipID.find(tags['open']),
         'end': tooltipID.find(tags['close'])}
        if indicies['start'] != -1 and indicies['end'] != -1:
            indicies['start'] += len(tags['open'])
            result += _getFormattedText(stripColorTagDescrTags(tooltipID[indicies['start']:indicies['end']]), tooltipBlock, formatType)

    return result


def doFormatData(data, formatType):
    result = []
    for kind in _TOOLTIP_KIND:
        if kind in data and data[kind] is not None:
            result.append(_getFormattedText(data[kind], kind.upper(), formatType))

    return ''.join(result)


def doFormatToolTip(tooltipID, formatType):
    if not tooltipID:
        return ''
    return _doFormatToolTipFromKey(tooltipID, formatType) if tooltipID.startswith('#') else _doFormatToolTipFromText(tooltipID, formatType)


def doAdvancedCounterText(text):
    return makeHtmlString(_HTML_COMPLEX, 'advanced_counter', {'text': text})
