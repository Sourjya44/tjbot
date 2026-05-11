import os
import tempfile
import unittest
from pathlib import Path

from config.schema_loader import ConfigSchemaError, load_config_schema


class SchemaLoaderTests(unittest.TestCase):
    def test_loads_schema_from_env_override(self):
        schema_text = """
type: object
properties:
    log:
        type: object
        description: Console logging configuration.
        properties:
            level:
                type: string
                enum: [info, debug]
                default: info
"""

        with tempfile.TemporaryDirectory() as tmpdir:
            schema_path = Path(tmpdir) / 'schema.yaml'
            schema_path.write_text(schema_text, encoding='utf-8')

            original = os.environ.get('TJBOT_CONFIG_SCHEMA_PATH')
            os.environ['TJBOT_CONFIG_SCHEMA_PATH'] = str(schema_path)
            try:
                schema = load_config_schema(required=True)
            finally:
                if original is None:
                    os.environ.pop('TJBOT_CONFIG_SCHEMA_PATH', None)
                else:
                    os.environ['TJBOT_CONFIG_SCHEMA_PATH'] = original

        section = schema.get_section('log')
        self.assertEqual(section.description, 'Console logging configuration.')
        properties = schema.get_object_properties(section.schema)
        self.assertEqual([item.key for item in properties], ['level'])

    def test_missing_env_override_fails_fast(self):
        original = os.environ.get('TJBOT_CONFIG_SCHEMA_PATH')
        with tempfile.TemporaryDirectory() as tmpdir:
            missing_path = Path(tmpdir) / 'missing.schema.yaml'
            os.environ['TJBOT_CONFIG_SCHEMA_PATH'] = str(missing_path)
            try:
                with self.assertRaises(ConfigSchemaError):
                    load_config_schema(required=True)
            finally:
                if original is None:
                    os.environ.pop('TJBOT_CONFIG_SCHEMA_PATH', None)
                else:
                    os.environ['TJBOT_CONFIG_SCHEMA_PATH'] = original


if __name__ == '__main__':
    unittest.main()
