import inspect
import sys
import os
import onyxexceptions as ex
import re
from functools import wraps
import time
import random
import string
import unicodedata


def exit_with_error(error="Non Specified Error"):
    """
        Terminates crawley with an error
    """
    print(error)
    sys.exit(1)


def search_class(base_klass, entities_list, return_class=False):
    for klass in entities_list:
        if issubclass(klass, base_klass) and not klass is base_klass:
            return klass


def check_for_file(settings, file_name):
    """
        Checks if a project file exists
    """

    return os.path.exists(os.path.join(settings.PROJECT_ROOT, file_name))


def fix_file_extension(file_name, extension):
    """
        Fixes the file extensions
    """

    if not file_name.endswith(".%s" % extension):
        file_name = "%s.%s" % (file_name, extension)
    return file_name


def add_to_path(path):
    """
        Adds the [path] variable to python path
    """
    if not path in sys.path:
        sys.path.insert(0, path)


def OnyxExceptionWrap():
    wrapException(ex.OnyxException(), "Onyx Spider General Exception")


def logException():
    import traceback
    from config.AppContext import getOnyxLogger

    log = getOnyxLogger()
    logIfPossible(traceback.format_exc(), log, 'error')


def wrapException(exceptionName, message):
    from config.AppContext import appContext

    trace = sys.exc_info()[2]
    try:
        value = appContext.getInstance().getValue("SHOW_DEBUG_INFO")
    except ex.ConfigError:
        value = 0
    if value == 1:
        logException()
    raise exceptionName(message).with_traceback(trace)


def benchmark(logger=None):
    """
    A decorator that prints the time a function takes
    to execute.
    """

    def decoBenchmark(func):
        import time

        def wrapper(*args, **kwargs):
            t = time.time()
            res = func(*args, **kwargs)
            if logger:
                logger.info(func.__name__, time.time() - t, 'secs wall time')
            else:
                print(func.__name__, time.time() - t, 'secs wall time')
            return res

        return wrapper

    return decoBenchmark

# Type checking

def isObjOfType(obj, _type):
    return type(obj) in ([_type] + _type.__subclasses__())


def bufferOptimalSize(IOSize):
    return 16384 if IOSize < 1 * 1024 * 1024 or IOSize == 0 else 32 * 1024


def reportRun(func):
    """
    A decorator that calls a reportRuntime method to report runtime.
    """

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        t = time.time()
        res = func(self, *args, **kwargs)
        self.reportRuntime(time.time() - t)
        return res

    return wrapper


def retry(ExceptionToCheck, tries=4, delay=3, backoff=2, logger=None):
    """Retry calling the decorated function using an exponential backoff.

    original from: http://wiki.python.org/moin/PythonDecoratorLibrary#Retry

    :param ExceptionToCheck: the exception to check. may be a tuple of
        exceptions to check
    :type ExceptionToCheck: Exception or tuple
    :param tries: number of times to try (not retry) before giving up
    :type tries: int
    :param delay: initial delay between retries in seconds
    :type delay: int
    :param backoff: backoff multiplier e.g. value of 2 will double the delay
        each retry
    :type backoff: int
    :param logger: logger to use. If None, print
    :type logger: logging.Logger instance
    """

    def deco_retry(f):

        @wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except ExceptionToCheck as e:
                    msg = "%s, Retrying in %d seconds..." % (str(e), mdelay)
                    if logger:
                        logger.warning(msg)
                    else:
                        print(msg)
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return f(*args, **kwargs)

        return f_retry  # true decorator

    return deco_retry


def delay(delayFactor=1, Mindelay=0, Indeviation=0):
    def decoDelay(f):
        @wraps(f)
        def delay(*args, **kwargs):
            import random
            import time

            FACTOR = 1000.0
            deviation = Indeviation * FACTOR
            randomize = random.randint(-deviation, deviation) / FACTOR
            delay = (Mindelay + randomize) * delayFactor
            time.sleep(delay)
            return f(*args, **kwargs)

        return delay

    return decoDelay


toKB = lambda bytes: bytes / 1024
toMB = lambda bytes: toKB(bytes) / 1024


def fixZeroResult(result):
    return 0.01 if result == 0 else result

# http://code.activestate.com/recipes/145672-multi-line-string-block-formatting/

def formatBlock(block):
    """Format the given block of text, trimming leading/trailing
    empty lines and any leading whitespace that is common to all lines.
    The purpose is to let us list a code block as a multiline,
    triple-quoted Python string, taking care of indentation concerns."""
    # separate block into lines
    lines = str(block).split('\n')
    # remove leading/trailing empty lines
    while lines and not lines[0]:  del lines[0]
    while lines and not lines[-1]: del lines[-1]
    # look at first line to see how much indentation to trim
    ws = re.match(r'\s*', lines[0]).group(0)
    if ws:
        lines = [x.replace(ws, '', 1) for x in lines]
        # remove leading/trailing blank lines (after leading ws removal)
    # we do this again in case there were pure-whitespace lines
    while lines and not lines[0]:  del lines[0]
    while lines and not lines[-1]: del lines[-1]
    return '\n'.join(lines) + '\n'


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def remove_accents(data):
    dataToProcess = str(data) if isObjOfType(data, str) else data
    return str(' '.join(''.join(x for x in unicodedata.normalize('NFD', d) if x in string.ascii_letters) for d in
                        dataToProcess.split(' ')))


isFileNull = lambda file: os.stat(file)[6] == 0

goodStatusCode = lambda code: 200 <= code < 300
#Logging

def logIfPossible(msg, logger=None, level='info'):
    if logger:
        try:
            log = getattr(logger, level)
            log(msg)
        except AttributeError:
            wrapException(ex.LoggerException, 'Invalid logger method')
    else:
        print(msg)


def logBeforeAfter(before, after, logger=None, level='info'):
    def deco_logBeforeAfter(f):
        @wraps(f)
        def f_logbefaft(*args, **kwargs):
            mbefore, mafter = before, after
            logIfPossible(mbefore, logger, level)
            ret = f(*args, **kwargs)
            logIfPossible(mbefore, logger, level)
            return ret

        return f_logbefaft

    return deco_logBeforeAfter


def timeNow():
    from datetime import datetime

    return datetime.now()


#Introspection

def getCurrentMethodName():
    """Auxiliary function to not to do DRY"""
    return inspect.stack()[1][3]