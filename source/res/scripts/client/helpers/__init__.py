# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/__init__.py
# Compiled at: 2011-05-14 18:13:47


def getClientLanguage():
    """
    Return client string of language code
    """
    import ResMgr
    lng = 'en'
    ds = ResMgr.openSection('text/settings.xml')
    if ds is not None:
        lng = ds.readString('clientLangID')
    return lng


def int2roman(number):
    """
    Convert arabic number to roman number
    @param number: int - number
    @return: string - roman number
    """
    numerals = {1: 'I',
     4: 'IV',
     5: 'V',
     9: 'IX',
     10: 'X',
     40: 'XL',
     50: 'L',
     90: 'XC',
     100: 'C',
     400: 'CD',
     500: 'D',
     900: 'CM',
     1000: 'M'}
    result = ''
    for value, numeral in sorted(numerals.items(), reverse=True):
        while 1:
            number >= value and result += numeral
            number -= value

    return result
