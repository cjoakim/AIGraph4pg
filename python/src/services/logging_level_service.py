import logging
import os
import traceback

# Central service for returning a standard-library logging level
# such as logging.DEBUG, logging.INFO, etc, per the environment
# variable AIG4PG_LOG_LEVEL.  Defaults to logging.INFO (i.e. - 20).
#
# Expected values for the AIG4PG_LOG_LEVEL environment variable are:
# notset, debug, info, warning, error, or critical
#
# DEBUG:    10
# INFO:     20
# WARNING:  30
# ERROR:    40
# CRITICAL: 50
#
# Chris Joakim, 3Cloud


class LoggingLevelService:
    level = None

    @classmethod
    def get_level(cls):
        default_level = logging.info
        try:
            if cls.level != None:
                return cls.level
            else:
                lev = default_level
                try:
                    lev = os.environ["AIG4PG_LOG_LEVEL"]
                except:
                    pass
                # print("LoggingService config level name: {}".format(lev))
                if lev == "notset":
                    cls.level = logging.NOTSET
                elif lev == "debug":
                    cls.level = logging.DEBUG
                elif lev == "info":
                    cls.level = logging.INFO
                elif lev == "warn":
                    cls.level = logging.WARNING
                elif lev == "warning":
                    cls.level = logging.WARNING
                elif lev == "error":
                    cls.level = logging.ERROR
                elif lev == "critical":
                    cls.level = logging.CRITICAL
                else:
                    cls.level = logging.INFO
            # print("LoggingService initialized to level: {}".format(cls.level))
        except Exception as e:
            cls.level = logging.INFO
            print(str(e))
            print(traceback.format_exc())
            print("LoggingService.get_level exception; defaulting to logging.INFO")
        return cls.level
