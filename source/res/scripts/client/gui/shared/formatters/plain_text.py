# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/formatters/plain_text.py
from gui.server_events.cond_formatters import FORMATTER_IDS
from gui.server_events import formatters
from gui.shared.formatters import text_styles

def getDefaultPlainTextFormatters():
    return {FORMATTER_IDS.SIMPLE_TITLE: formatters.titleFormatPlain,
     FORMATTER_IDS.CUMULATIVE: formatters.titleCumulativeFormatPlain,
     FORMATTER_IDS.COMPLEX: formatters.titleComplexFormatPlain,
     FORMATTER_IDS.RELATION: formatters.titleRelationFormatPlain,
     FORMATTER_IDS.DESCRIPTION: text_styles.highlightTextPlain,
     FORMATTER_IDS.COMPLEX_RELATION: formatters.titleComplexRelationFormatPlain}


class PlainTextFormatter(object):
    _formatters = getDefaultPlainTextFormatters()

    @classmethod
    def getPlainTextFromFormattedField(cls, formattableField):
        formatterName = formattableField.formatterID
        formatter = cls._formatters.get(formatterName)
        text = formatter(*formattableField.args)
        return text
