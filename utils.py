from contextlib import contextmanager

import os
import re
import pickle
import tempfile
import configparser

# global settings
# -----------------------------------------------------------------------------
class ConfigFromFile(object):
    """
    Read configuration options from a config file
    (e.g., arxiv-sanity.cfg) using ConfigParser.
    Populate config variables as members of this class,
    so you can access with, e.g., Config2().db_path.
    
    We also define `Config = Config2()` in this file,
    so you can just `from utils import Config; Config.db_path`,
    just like the existing code.
    """
    def __init__(self, config_file='arxiv-sanity.cfg'):
        self.config_file = config_file

        parser = configparser.ConfigParser()
        parser.read(config_file)
        self.parser = parser

        self._check_config()
        self._populate_vars()

    def _check_config(self):
        if not self.parser.has_section('arxiv-sanity'):
            raise ValueError("Config file {0} doesn't have section "
                    "[arxiv-sanity]".format(self.config_file))

    def _populate_vars(self):
        vars_list = ['data_root',
                     'db_path',
                     'pdf_dir',
                     'txt_dir',
                     'thumbs_dir',
                     'tfidf_path',
                     'meta_path',
                     'sim_path',
                     'user_sim_path',
                     'db_serve_path',
                     'database_path',
                     'serve_cache_path',
                     'beg_for_hosting_money',
                     'banned_path',
                     'tmp_dir',
                     ]
        
        parser = self.parser # alias
        for var in vars_list:
            val = parser.get('arxiv-sanity', var)
            setattr(self, var, val)
# Doing this should work with the old class var Config class
# without changing the rest of the code
Config = ConfigFromFile()


# Context managers for atomic writes courtesy of
# http://stackoverflow.com/questions/2333872/atomic-writing-to-file-with-python
@contextmanager
def _tempfile(*args, **kws):
    """ Context for temporary file.

    Will find a free temporary filename upon entering
    and will try to delete the file on leaving

    Parameters
    ----------
    suffix : string
        optional file suffix
    """

    fd, name = tempfile.mkstemp(*args, **kws)
    os.close(fd)
    try:
        yield name
    finally:
        try:
            os.remove(name)
        except OSError as e:
            if e.errno == 2:
                pass
            else:
                raise e


@contextmanager
def open_atomic(filepath, *args, **kwargs):
    """ Open temporary file object that atomically moves to destination upon
    exiting.

    Allows reading and writing to and from the same filename.

    Parameters
    ----------
    filepath : string
        the file path to be opened
    fsync : bool
        whether to force write the file to disk
    kwargs : mixed
        Any valid keyword arguments for :code:`open`
    """
    fsync = kwargs.pop('fsync', False)

    with _tempfile(dir=os.path.dirname(filepath)) as tmppath:
        with open(tmppath, *args, **kwargs) as f:
            yield f
            if fsync:
                f.flush()
                os.fsync(file.fileno())
        os.rename(tmppath, filepath)

def safe_pickle_dump(obj, fname):
    with open_atomic(fname, 'wb') as f:
        pickle.dump(obj, f, -1)


# arxiv utils
# -----------------------------------------------------------------------------

def strip_version(idstr):
    """ identity function if arxiv id has no version, otherwise strips it. """
    parts = idstr.split('v')
    return parts[0]

# "1511.08198v1" is an example of a valid arxiv id that we accept
def isvalidid(pid):
  return re.match('^\d+\.\d+(v\d+)?$', pid)
