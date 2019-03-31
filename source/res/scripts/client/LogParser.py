# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/LogParser.py
# Compiled at: 2010-09-28 12:58:18
from debug_utils import LOG_DEBUG, LOG_ERROR, LOG_CURRENT_EXCEPTION
import BigWorld, Settings, Event, pickle, base64, os, re, datetime
KEY_LOG_PARSER_POSITION = 'logParserPosition'
LOG_MATCH_PATTERNS = ('\\[(?P<type>.+)\\] (?P<string>.+)', '(?P<type>.+) \\(most recent call last\\)(?P<string>):')

class LogObject(object):

    def __init__(self):
        pass

    def __str__(self):
        pass

    def __eq__(self, other):
        return False


class LogError(LogObject):
    MATCH_PATTERN = '\\((?P<path>.+), (?P<line>[0-9]*)\\): (?P<message>.+)'

    def __init__(self, string_line, file):
        result = re.match(self.MATCH_PATTERN, string_line)
        if result is not None:
            group = result.groupdict()
            self.file = group['path']
            self.line = group['line']
            self.message = group['message']
        return

    def __str__(self):
        return 'ERROR - message: %s, file: %s, line: %s' % (self.message, self.file, self.line)

    def __eq__(self, other):
        return isinstance(other, LogError) and self.file == other.file and self.line == other.line and self.message == other.message


class LogTraceback(LogObject):
    MATCH_PATTERN = '(?P<error>.+): (?P<message>.+)'

    def __init__(self, string_line, file):
        result = None
        self.trace = ''
        while 1:
            l = result is None and file.next()
            self.trace += l
            result = re.match(self.MATCH_PATTERN, l)

        group = result.groupdict()
        self.error = group['error']
        self.message = group['message']
        return

    def __str__(self):
        return 'TRACEBACK - type: %s, message: %s' % (self.error, self.message)

    def __eq__(self, other):
        return isinstance(other, LogTraceback) and self.error == other.error and self.message == other.message


class LogException(LogObject):
    MATCH_PATTERN = '\\((?P<path>.+), (?P<line>[0-9]*)\\):'

    def __init__(self, string_line, file):
        result = re.match(self.MATCH_PATTERN, string_line)
        if result is not None:
            group = result.groupdict()
            self.path = group['path']
            self.line = group['line']
        string_line = file.next()
        self.traceback = LogTraceback(string_line, file)
        return

    def __str__(self):
        return 'EXCEPTION - file: %s, line: %s, trace: %s' % (self.path, self.line, self.traceback)

    def __eq__(self, other):
        return isinstance(other, LogException) and self.path == other.path and self.line == other.line and self.traceback == other.traceback


class LogWarning(LogObject):
    MATCH_PATTERN = '\\((?P<path>.+), (?P<line>[0-9]*)\\): (?P<message>.+)'

    def __init__(self, string_line, file):
        result = re.match(self.MATCH_PATTERN, string_line)
        if result is not None:
            group = result.groupdict()
            self.file = group['path']
            self.line = group['line']
            self.message = group['message']
        return

    def __str__(self):
        return 'WARNING -  message: %s, file: %s, line: %s' % (self.message, self.file, self.line)

    def __eq__(self, other):
        return isinstance(other, LogWarning) and self.file == other.file and self.line == other.line and self.message == other.message


class LogParser(object):
    LOG_OBJECTS_CORRESPONDENCE = {'ERROR': LogError,
     'EXCEPTION': LogException,
     'Traceback': LogTraceback}

    @staticmethod
    def __readSection(ds, name):
        if not ds.has_key(name):
            ds.write(name, '')
        return ds[name]

    @staticmethod
    def parse(path):
        result_file = open('parser.log', 'a+')
        result_file.write('\n------------------------ Start new parsing at %s\n' % datetime.datetime.now().strftime('%H:%M:%S %m/%d/%Y'))
        list_dir = os.listdir(path)
        for entry in list_dir:
            filepath = '%s/%s' % (path, entry)
            file = open(filepath, 'r')
            try:
                results = LogParser.__parse(file)
                result_file.write('file: %s\n' % filepath)
                for obj in results:
                    result_file.write('%s, count: %d\n' % (str(obj), results[obj]))

            finally:
                LogParser.__afterParse(file)

        result_file.close()

    @staticmethod
    def __afterParse(file):
        if file:
            file.close()

    @staticmethod
    def __processString(string):
        for pattern in LOG_MATCH_PATTERNS:
            result = re.match(pattern, string)
            if result is not None:
                return result.groupdict()

        return

    @staticmethod
    def __parse(file):
        if file is not None:
            results = {}
            for line in file:
                d = LogParser.__processString(line)
                if d is not None:
                    log_object_instance = LogParser.LOG_OBJECTS_CORRESPONDENCE.get(d['type'], None)
                    if log_object_instance is not None:
                        obj = log_object_instance(d['string'], file)
                        for key in results:
                            if obj == key:
                                results[key] += 1
                                break
                        else:
                            results[obj] = 1

            return results
        else:
            return
