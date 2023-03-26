"""Provide configuration storage.

The configuration file template is normally put in `config_default.yaml` inside
the module directory.
"""

from __future__ import annotations

import os
import sys
from typing import TextIO

import confuse


class Config:
    """Provide configuration storage.

    Attributes:
        config: the basic configuration object
        vconf: the parsed and validated configuration object
    """

    def __init__(
            self, app_name: str | None = None, mod_name: str | None = None,
            template: dict[str, confuse.Template] | None = None
            ) -> None:
        """Initialize the configuration object.

        Args:
            app_name: application name
            mod_name: module name, this parameter is needed to find the default
                configuration file `config_default.yaml`
            template: template for validating the configuration

        Fixme:
            - Make template mandatory?
            - Provide a default for mod_name?
            - Test behavior without app_name.
        """
        if app_name is None:
            app_name = os.path.basename(sys.argv[0])
        self.template = template
        # self.config = confuse.LazyConfig(app_name, mod_name)
        self.config = confuse.Configuration(app_name, mod_name)
        self.validate()
        # self.config.set_file(config_file)
        # self.config.set_args()

    def validate(self) -> None:
        """Validate the configuration using the template."""
        vconf = self.config.get(self.template)
        assert isinstance(vconf, confuse.AttrDict)
        self.vconf: confuse.AttrDict = vconf

    def get_user_dirname(self) -> str:
        """Get user's configuration directory name."""
        return self.config.config_dir()
        # FIXME: test .user_config_path()

    def get_user_filename(self) -> str:
        """Get user's configuration file name."""
        return os.path.join(self.get_user_dirname(), confuse.CONFIG_FILENAME)
        # FIXME: fix upstream: confuse.CONFIG_FILENAME not documented

    def write(self, only_new: bool = True) -> None:
        """Save configuration to user's store.

        Args:
            only_new: Write the configuration file only if it does not exist.

        Todo:
            - dump with comments
                - The dump() method of confuse.Configuration contains code
                    to dump the configuration with comments.
                - Only comments without whitespace at the beginning of the line
                    are dumped. Bug?
            - get the `config_default.yaml` file path; inside confuse:
                - self._package_path = util.find_package_path(self.mod_name)
                - os.path.join(self._package_path, DEFAULT_FILENAME)
        """
        user_fname = self.get_user_filename()
        if not only_new or not os.path.exists(user_fname):
            with open(user_fname, 'w', encoding='utf-8') as conf_file:
                conf_file.write(self.config.dump())
            # logging.info("Configuration written to %s.", user_fname)

    def dbg_print(self, stream: TextIO = sys.stderr) -> None:
        """Print the configuration."""
        print('######### Configuration debug print:', file=stream)
        print('--- config:', self.config, sep='\n', file=stream)
        print('--- vconf:', self.vconf, sep='\n', file=stream)
        print('--- dump:', self.config.dump(), sep='\n', file=stream)
        print('--- get_user_dirname():', self.get_user_dirname(), file=stream)
        print(
                '--- get_user_filename():', self.get_user_filename(),
                file=stream)
