import unittest
from unittest.mock import patch

import tomlkit

from config.schema_loader import load_config_schema
from config.wizard import TJBotConfigEditor


class WizardSchemaIntegrationTests(unittest.TestCase):
    @patch('config.wizard.get_system_info', return_value={})
    def test_top_level_sections_come_from_schema(self, _mock_system_info):
        schema = load_config_schema(required=True)
        editor = TJBotConfigEditor(tomlkit.document(), schema=schema)

        sections = editor._available_sections()

        self.assertEqual(
            [key for _label, key in sections],
            ['log', 'hardware', 'listen', 'see', 'shine', 'speak', 'wave'],
        )
        self.assertIn('Logging configuration.', sections[0][0])


if __name__ == '__main__':
    unittest.main()