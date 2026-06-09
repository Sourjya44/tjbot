import unittest

from config.schema_loader import load_config_schema
from config.validators import validate_config


class ValidatorTests(unittest.TestCase):
    def test_schema_validation_catches_type_mismatch(self):
        schema = load_config_schema(required=True)
        config = {
            'log': {'level': 'info'},
            'listen': {'microphoneRate': '44100'},
        }

        result = validate_config(config, schema=schema)

        self.assertFalse(result.valid)
        self.assertTrue(
            any('listen.microphoneRate' in error and 'not of type' in error for error in result.errors)
        )


if __name__ == '__main__':
    unittest.main()