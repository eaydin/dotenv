import shutil
import tempfile
import os
from collections import Counter


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
    comment=None
    if '=' not in line:
        value = True
        return value, comment
    else:

        # if ends with comments, take them out
        # if sameline comments are NOT seperated by a whitespace
        # they are considered part of the value
        if " #" in line:
            comment = "#" + line.split(" #")[1].strip()
            line = line.split(" #")[0]
        elif " //" in line:
            comment = "//" + line.split(" //")[1].strip()
            line = line.split(" //")[0]
        elif " ;" in line:
            comment = ";" + line.split(" ;")[1].strip()
            line = line.split(" ;")[0]

        columns = line.split('=')

        if len(columns) == 2:
            if columns[1] == '':
                value = ''
                return value, comment
            else:
                value = columns[1]
                return value.strip(), comment
        else:
            value = '='.join(columns[1:])
            return value.strip(), comment


class Environment(object):
    def_file_path = '.env'

    def __init__(self, file_path=def_file_path):
        self.stat = False
        self.file_path = file_path
        self.backup_file_name = ''
        self.backup_file()
        self.env = {}

        self.keys = []
        self.values = []
        self.comments = []
        self.lines = []

        self.read_env()

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

    def read_env(self):
        if self.stat:
            lines = self.read_from_file()
            self.parse_env(lines)

    def parse_env(self, env_lines):

        for num, line in enumerate(env_lines):

            line = line.strip()
            if len(line) > 0:
                if line[0] == "#" or line[0] == ';' or line[:2] == '//':
                    # this is a commented line
                    self.lines.append(num)
                    self.comments.append(line)
                    self.keys.append(None)
                    self.values.append(None)
                else:
                    # we have values here
                    keys = _get_keys_from_line(line)
                    value, comment = _get_value_from_line(line)

                    for key in keys:
                        if key != '':
                            self.keys.append(key)
                            self.values.append(value)
                            self.lines.append(num)
                            self.comments.append(comment)

            else:
                # empty line
                self.keys.append(None)
                self.values.append(None)
                self.lines.append(num)
                self.comments.append(None)
        self.refresh_env()

    def refresh_env(self):
        self.env = {}
        self.env = dict(zip(self.keys, self.values))

    def _refresh_lists(self):
        for key in self.env:
            if not key in self.keys:
                self.keys.append(key)
                self.values.append(self.env[key])
                self.lines.append(max(self.lines)+1)
                self.comments.append(None)

            else:
                idx = self.keys.index(key)
                self.values[idx] = self.env[key]

        self._reorganize()

    def _reorganize(self):

        # lines with multiple values
        mult = [ k for k,v in Counter(self.lines).items() if v > 1 ]
        if len(mult) > 0:
            for item in mult:
                # this is the index number of line element
                idxs = [i for i,j in enumerate(self.lines) if j == item]

                # now check for values in this index, if they are not same, split them apart
                idxs = tuple(idxs)

                vals = [i for i in map(self.values.__getitem__, idxs)]

                # if all of them are them same (none changed)
                if len(Counter(vals)) == 1:
                    pass
                else:
                    # we have multiple values for this single line
                    # we'll keep the values with highest frequency
                    # rest will be added to new lines
                    # --- the above expression is not done yet ----
                    # instead, we simply divide keys if they are not all equal
                    for i,j in enumerate(idxs):
                        # we keep the first line as is
                        if i != 0:
                            # we add 1 to each following line numbers
                            self.lines = self.lines[:j] + [x+1 for x in self.lines[j:]]

    def _create_line(self, line):

        new_line = ""

        # get id of the list for line number
        idxs = [i for i,j in enumerate(self.lines) if j == line]
        idxs = tuple(idxs)

        # get keys for those id's which are not None
        keys = [i for i in map(self.keys.__getitem__, idxs) if i]
        # get values for those id's which are not None
        values = [i for i in map(self.values.__getitem__, idxs) if i]
        # get comments for those id's which are not None
        comments = [i for i in map(self.comments.__getitem__, idxs) if i]

        if len(keys) == 1:
            # we have a single key
            new_line = str(keys[0])
        elif len(keys) > 1:
            # we have multiple keys for this line
            new_line = " ,".join(keys)
        elif len(keys) == 0:
            # no keys for this line
            new_line = ""

        if len(values) > 0:
            # we have values for this (or these) key(s)
            new_value = str(values[0])
            new_line += " = {0}".format(new_value)

        if len(comments) > 0:
            # add a space if we already have keys
            if new_line != "":
                new_line += " "
            # we take only one of the comments at this point
            # usually they all end up being the same line
            new_line += comments[0]

        new_line += "\n"

        return new_line

    def update_file(self):
        # print("Backup filename is : {0}".format(self.backup_file_name))
        if self.stat:
            with open(self.file_path, 'w') as fp:
                for line in range(max(self.lines)+1):
                    fp.write(self._create_line(line))

if __name__ == '__main__':
    print("Line |  Keys")
    print("------------------")
    a = Environment()
    if a.stat:
        for i in range(max(a.lines)+1):
            print("{0:4d}    {1}".format(i, a._create_line(i)[:-1]))
    print("------------------")