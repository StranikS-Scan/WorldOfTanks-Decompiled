# Embedded file name: scripts/client/gui/Scaleform/CommandArgsParser.py


class CommandArgsParser(object):

    def __init__(self, callbackName, count = 0, converters = None):
        self.__callbackName = callbackName
        self.__count = count
        self.__converters = converters if converters is not None else []
        self.__responseID = None
        self.__responseArgs = []
        return

    def parse(self, *args):
        self.__responseID = args[0]
        self.__responseArgs = []
        self.__responseArgs.append(self.__responseID)
        result = []
        convertersLen = len(self.__converters)
        if len(args) == self.__count + 1:
            for index in xrange(1, len(args)):
                if convertersLen >= index:
                    result.append(self.__converters[index - 1](args[index]))
                else:
                    result.append(args[index])

            return result
        raise ValueError, 'Callback %s takes %d arguments' % (self.__callbackName, self.__count)

    def addArgs(self, values, converters = None):
        if converters is None:
            converters = []
        parsed = map(lambda item: (converters[item[0]](item[1]) if len(converters) > item[0] else item[1]), enumerate(values))
        self.__responseArgs.extend(parsed)
        return

    def addArg(self, value, converter = None):
        parsed = converter(value) if converter else value
        self.__responseArgs.append(parsed)

    def args(self):
        return self.__responseArgs
