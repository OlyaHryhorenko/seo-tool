import ConfigParser
import os
config = ConfigParser.RawConfigParser()


class Conf:

    """class Conf for writing and reading config DB"""

    def __init__(self, section="MySQL"):
        self.section = section
        APP_ROOT = os.path.dirname(os.path.abspath(__file__))
        self.file_name = os.path.join(APP_ROOT, '../config/conf.cfg')

    def write(self):
        config.add_section(self.section)
        config.set(self.section, "host", "104.236.221.57")
        config.set(self.section, "user", "root")
        config.set(self.section, "password", "26klsU2gb3u30")
        config.set(self.section, "db", "seo_dev")
        with open(self.file_name, "wb") as config_file:
            config.write(config_file)

    def read(self):
        config.read(self.file_name)
        return [config.get(self.section, "host"), config.get(self.section, "user"),
                config.get(self.section, "password"), config.get(self.section, "db")]

    def write_sqlite(self):
        config.add_section(self.section)
        config.set(self.section, "name", "MainDB.db")
        with open(self.file_name, "wb") as config_file:
            config.write(config_file)

    def read_sqlite(self):
        config.read(self.file_name)
        return config.get(self.section, "name")
