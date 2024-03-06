# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/hints_common/common/manager.py
import typing
import logging
import importlib
import section2dict
from extension_utils import ResMgr
from dict2model import exceptions
if typing.TYPE_CHECKING:
    from dict2model.models import Model
    from dict2model.schemas import Schema
_logger = logging.getLogger(__name__)
SCHEMA_NAME_DELIMITER = ':'
HINTS_TAG = 'hint'
SCHEMA_TAG = 'schema'

def _readHintsXml(xmlPath):
    section = ResMgr.openSection(xmlPath)
    if section is None:
        _logger.error('Broken xml schemas source: %s.', xmlPath)
        return
    else:
        hints = section2dict.parse(section).get(HINTS_TAG, [])
        if not isinstance(hints, list):
            hints = [hints]
        if not hints:
            _logger.debug('File <%s> section [%s] empty or does not exist.', xmlPath, HINTS_TAG)
        ResMgr.purge(xmlPath, True)
        return hints


class BaseHintsModelsManager(object):
    __slots__ = ('_importedSchemas', '_defaultSchema', '_schemaTag')

    def __init__(self, xmlPath, defaultSchema, schemaTag=SCHEMA_TAG):
        self._schemaTag = schemaTag
        self._importedSchemas = {}
        self._defaultSchema = defaultSchema
        self._registerFromXml(xmlPath)

    def _registerFromXml(self, xmlPath):
        errors = None
        for index, rawHintData in enumerate(_readHintsXml(xmlPath)):
            try:
                schemaLocation = rawHintData.pop(self._schemaTag, '') if isinstance(rawHintData, dict) else ''
                schema = self._importSchema(schemaLocation) if schemaLocation else self._defaultSchema
                self._register(schema, rawHintData)
            except exceptions.ValidationError as ve:
                error = exceptions.ValidationErrorMessage(ve.error.data, title='Hint[{}]'.format(index))
                errors = errors + error if errors else error

        try:
            self._validateRegistered()
        except exceptions.ValidationError as ve:
            error = exceptions.ValidationErrorMessage(ve.error.data, title='Validate registered models')
            errors = errors + error if errors else error

        if errors:
            raise exceptions.ValidationError(errors)
        return

    def _register(self, schema, rawHintData):
        self._checkSchemaType(schema)
        hint = schema.deserialize(rawHintData, silent=False)
        self._addToStorage(schema, hint)

    def _importSchema(self, location):
        if not isinstance(location, str):
            raise exceptions.ValidationError('Wrong schema location type. {} != str.'.format(type(location)))
        if location in self._importedSchemas:
            return self._importedSchemas[location]
        else:
            locationParts = location.split(SCHEMA_NAME_DELIMITER)
            if len(locationParts) != 2:
                raise exceptions.ValidationError('Wrong schema location format. Example: schemas.base:magicSchema.')
            modulePath, name = locationParts
            try:
                module = importlib.import_module(modulePath)
            except ImportError:
                raise exceptions.ValidationError('Wrong schema module path: {}.'.format(modulePath))

            schema = getattr(module, name, None)
            if schema is None:
                raise exceptions.ValidationError('Wrong schema variable name: {}.'.format(name))
            self._checkSchemaType(schema)
            self._importedSchemas[location] = schema
            return self._importedSchemas[location]

    def _addToStorage(self, schema, model):
        raise NotImplementedError

    def _checkSchemaType(self, schema):
        raise NotImplementedError

    def _validateRegistered(self):
        pass
