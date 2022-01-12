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
            self, appname: str | None = None, modname: str | None = None,
            template: dict[str, confuse.Template] | None = None
            ) -> None:
        """Initialize the configuration object.

        Args:
            appname: application name
            modname: module name, this parameter is needed to find the default
                configuration file `config_default.yaml`
            template: template for validating the configuration

        Fixme:
            - Make template mandatory?
            - Provide a default for modname?
            - Test behavior without appname.
        """
        if appname is None:
            appname = os.path.basename(sys.argv[0])
        self.template = template
        # self.config = confuse.LazyConfig(appname, modname)
        self.config = confuse.Configuration(appname, modname)
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
                - Only comments withoud whitespace at the beginning of the line
                    are dumped. Bug?
            - get the `config_default.yaml` file path; inside confuse:
                - self._package_path = util.find_package_path(self.modname)
                - os.path.join(self._package_path, DEFAULT_FILENAME)
        """
        user_fname = self.get_user_filename()
        if not only_new or not os.path.exists(user_fname):
            with open(user_fname, 'w') as conf_file:
                conf_file.write(self.config.dump())
            # logging.info("Configuration written to %s.", user_fname)

    def dbg_print(self, stream: TextIO = sys.stderr) -> None:
        """Print the configuration."""
        print('######### Configuration debug print:')
        print('--- config:', self.config, sep='\n')
        print('--- vconf:', self.vconf, sep='\n')
        print('--- dump:', self.config.dump(), sep='\n')
        print('--- get_user_dirname():', self.get_user_dirname())
        print('--- get_user_filename():', self.get_user_filename())
