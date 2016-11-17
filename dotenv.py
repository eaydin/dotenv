import shutil
import tempfile
import os


class Error(Exception):
    """Base class for custom exceptions"""
    pass


class NoEnvFile(Error):
    """Env file doesn't exists"""
    pass


def _get_keys_from_line(line):
    """Parses the keys from incoming line"""
    _keys = []
    keys = []
    if '=' in line:
        key_line = line.split('=')[0].strip()
    else:
        # No Equal Sign
        key_line = line.strip()

    # # Uppercase the keys
    # key_line = key_line.upper()

    # Split keys if comma separated
    if ',' in key_line:
        _keys = key_line.split(',')
    else:
        _keys.append(key_line)

    # Check for spaces in keys
    for key in _keys:
        key = key.strip()

        if ' ' in key:
            keys.append('_'.join(key.split()))
        else:
            keys.append(key)

    return keys


def _get_value_from_line(line):
    """Parses the values from incoming line"""
    if '=' not in line:
        value = True
        return value
    else:
        columns = line.split('=')

        if len(columns) == 2:
            if columns[1] == '':
                value = False
                return value
            else:
                value = columns[1]
                return value.strip()
        else:
            value = '='.join(columns[1:])
            return value.strip()


class Environment(object):
    def_file_path = '.env'

    def __init__(self, file_path=def_file_path):
        self.stat = False
        self.file_path = file_path
        self.backup_file_name = ''
        self.backup_file()
        self.env = {}
        self.comments = []
        self.refresh_env()

    def backup_file(self):
        try:
            if not os.path.isfile(self.file_path):
                raise NoEnvFile
            else:
                tmp_file = tempfile.NamedTemporaryFile(prefix='env-bak-', delete=False)
                tmp_file.close()
                self.backup_file_name = tmp_file.name
                shutil.copyfile(self.file_path, self.backup_file_name)
                self.stat = True
        except NoEnvFile:
            print("Error: Environment file doesn't exists at: {0}".format(self.file_path))
            self.stat = False
        except Exception as err:
            print("Error: {0}".format(str(err)))
            self.stat = False

    def read_from_file(self):
        try:
            with open(self.file_path, 'r') as env_file:
                env_lines = env_file.readlines()
            return env_lines
        except Exception as err:
            print("Error: {0}".format(str(err)))

    def refresh_env(self):
        if self.stat:
            lines = self.read_from_file()
            self.parse_env(lines)

    def parse_env(self, env_lines):
        env = {}

        for line in env_lines:
            line = line.strip()
            if len(line) > 0:
                if line[0] == "#" or line[0] == ';' or line[:2] == '//':
                    # this is a commented line
                    self.comments.append(line)
                    pass
                else:
                    keys = _get_keys_from_line(line)
                    value = _get_value_from_line(line)

                    for key in keys:
                        if key != '':
                            env[key] = value

            else:
                # empty line
                pass
        self.env = env

    def update_file(self):
        print("Backup filename is : {0}".format(self.backup_file_name))
        if self.stat:
            with open(self.file_path, 'w') as fp:
                if len(self.comments) > 0:
                    fp.writelines('\n'.join(self.comments))
                    # Empty line after comments
                    fp.write("\n\n")
                for key in self.env:
                    fp.write("{key} = {value}\n".format(key=key, value=self.env[key]))

if __name__ == '__main__':
    print("Testing to printout")
    a = Environment()
    if a.stat:
        for i in a.env:
            print("{0} = {1}".format(i, a.env[i]))