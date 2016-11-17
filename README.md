# dotenv
Manipulate .env files in Python

## Motive

There are numerous .env handlers for Python out there, yet none of them answered my needs so I wrote a quick-dirty solution. This may or may not be what you need, I encourage searching for alternatives before using it.

## Features

* Backup the .env file before operations
* Access .env variables as Python dictionaries
* Add / delete / update values from .env files
* Understand values with = in them
* Ignore (and preserve) comment lines
* Translates whitespaces in KEY names to _ underscores 
* Understands multiple declarations delimited with commas in the same line

## Installation

After cloning the repo, simply install.

```python setup.py install```

## Usage

Import dotenv and create an Environment class

```
>>> from dotenv import dotenv
>>> my_env = dotenv.Environment('/path/to/.env')
>>> for i in my_env.env: print("{0} = {1}".format(i, my_env.env[i]))
...
DB_PASSWORD = supersecret
APP_ENV = local
MAIL_PORT = 2525
MAIL_ENCRYPTION = none
>>> my_env.env['NEW_VALUE']=999
>>> my_env.update_file()
# if for somereason the file is changed
# and you want to refresh your dictionary
>>> my_env.refresh_env()
```

## Comments

* Lines starting with # ; and // are considered comments and are ignored.
* Comments are saved in an alternative list to be preserved after re-writing.
* The order of comments are NOT preserved. All comments are moved to the top of the file, with an empty line following them to seperate from the KEY=VALUE pairs
* Comments cannot be in the same line with the declarations (meaning, ```DB_USER=localhost # this is databaseusername``` is illegal)

## Declarations
* This is a valid declaration:
```USER1, USER2, USER3 = localhost```
All variables in that line will be "localhost"
* This is also valid
```DO_BACKUP, DO_LOGROTATE```
Notice there aren't any = signs, in this case, both variables are set to TRUE.
* On the other hand, the following case would set the variables to FALSE:
```DO BACKUP, DO LOGROTATE=```
There are two points to case in this example. First of all, if there is a = sign but the values are not SET to anything, the script assumes the values are False (as in, there used to be a value but not anymore, so it should be False). Second point is that, the KEY values are seperated by commands but they don't contain and understand, the script will replace the whitespaces automatically, resulting in ```DO_BACKUP=FALSE``` and ```DO_LOGROTATE=FALSE```
