import os
import re

import exetest
from filereader import load_json

# load global BUILD_TYPE_CFG which is used liberally below
# and would be inefficient to constantly reload
BUILD_TYPE_CFG = load_json(
    os.path.join(exetest.get_main_dir(), "config/buildconfig.json"))


class BuildConfig:
    """Represents a build config dictionary and provides .get() for access."""

    def __init__(self, build_type):
        self.build_type = build_type
        self.config = BUILD_TYPE_CFG[build_type]

    def get(self, label, forkey=None):
        """
        Returns build configuration value for given label in the build_type
        section associated with this instance.

        When forkey is specified, the key from the build type section's
        "custom" subsection will be used if forkey matches said custom
        key when treating said custom key as a regex pattern.
        """
        if forkey:
            custom = self.config.get('custom') or {}
            for k in custom:
                if re.match(k, forkey):
                    if label in custom[k]:
                        # return custom-subsection config value
                        return custom[k][label]

        # return standard config value of this build type
        return self.config.get(label)


def get_full_build_type_name(build_type):
    if build_type == 'd':
        return 'dig'
    if build_type == 'b':
        return 'build'
    if build_type == 'p':
        return 'place'
    if build_type == 'q':
        return 'query'
    return build_type
