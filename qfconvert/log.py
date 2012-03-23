import functools
import types

from errors import LogError

__LOG_LEVELS = []


def set_log_levels(levels):
    global __LOG_LEVELS

    if levels is None:
        return

    for level in levels:
        if level not in __LOG_LEVELS:
            __LOG_LEVELS += [level]


def unset_log_level(level):
    global __LOG_LEVELS
    if level in __LOG_LEVELS:
        __LOG_LEVELS.remove(level)


def log_routine(level, label):
    """Decorator to login BEGIN and END of an outer/major method execution."""
    def factory(func):
        @functools.wraps(func)
        def decorator(*args, **kwargs):
            if level not in __LOG_LEVELS:
                return func(*args, **kwargs)

            print '>>>> BEGIN ' + label
            result = func(*args, **kwargs)
            print '<<<< END ' + label
            return result
        return decorator
    return factory


def logmsg(level, message):
    """Call to log a single message out."""
    global __LOG_LEVELS
    if level in __LOG_LEVELS:
        if isinstance(message, str):
            print '#### ' + message
        elif isinstance(message, types.FunctionType):
            print '#### ' + message()
        else:
            raise LogError("Error in logmsg")
    return


def loglines(level, lines):
    """Call to log 1+ lines out without modification."""
    global __LOG_LEVELS
    if level in __LOG_LEVELS:
        if isinstance(lines, str):
            print lines
        elif isinstance(lines, types.FunctionType):
            print lines()
        else:
            raise LogError("Error in loglines")
    return
