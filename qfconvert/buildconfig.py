import json
import re

# load global BUILD_TYPE_CF which is used liberally below and would be inefficient to constantly reload
with open("buildconfig.json") as f:
    BUILD_TYPE_CFG = json.load(f)


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

