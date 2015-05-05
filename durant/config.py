import os

from durant.exceptions import ConfigError

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

DURANT_FILE = 'durant.conf'
DURANT_DIR = '.durant/'
DURANT_RELEASES_DIR = DURANT_DIR + 'releases/'


class Config(object):
    project_path = None
    config_path = None
    config = None

    def __init__(self, project_path=None):
        if not project_path:
            self.project_path = os.getcwd()

        self.config_path = os.path.realpath(
            os.path.join(self.project_path, DURANT_FILE))

        if not os.path.exists(self.config_path):
            raise ConfigError("Config file '%s' not found" % DURANT_FILE)

        try:
            self.config = configparser.ConfigParser()
            self.config.read_file(open(self.config_path))
        except:
            self.config = configparser.SafeConfigParser()
            self.config.readfp(open(self.config_path))

    def get(self, section, key, many=False, fallback=None):
        try:
            raw_value = self.config.get(section, key)
        except configparser.NoOptionError:
            raw_value = fallback

        if raw_value and many:
            value = raw_value.splitlines(
            ) if '\n' in raw_value else raw_value.split(',')
            return filter(None, map(str.strip, value))

        return raw_value

    def has_stage(self, stage):
        return self.config.has_section(stage)
