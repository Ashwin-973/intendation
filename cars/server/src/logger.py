
from __future__ import annotations

import sys
import logging
from datetime import datetime,UTC
from typing import Any


class ShelbyFormatter(logging.Formatter):
    """
    Emits log records as structured text lines:
        [2025-01-15T10:30:00Z] LEVEL     logger_name  │ message  {extra…}
    """

    LEVEL_COLORS={
        "DEBUG":    "\033[36m",   # cyan
        "INFO":     "\033[32m",   # green
        "WARNING":  "\033[33m",   # yellow
        "ERROR":    "\033[31m",   # red
        "CRITICAL": "\033[35m",   # magenta
    }

    RESET = "\033[0m"

    def format(self,record:logging.LogRecord)->str:
        #ISO to UTC
        ts=datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

        level=record.levelname
        color=self.LEVEL_COLORS.get(level,"")
        
        extras:dict[str,Any]={}
        for key,value in record.__dict__.items():
            if key not in {
                "name", "msg", "args", "levelname", "levelno",
                "pathname", "filename", "module", "exc_info",
                "exc_text", "stack_info", "lineno", "funcName",
                "created", "msecs", "relativeCreated", "thread",
                "threadName", "processName", "process", "message",
                "taskName",
            }:
                extras[key]=value

        extra_str="  "+"  ".join(f"{k}={v!r}" for k,v in extras.items()) if extras else ""

        msg=record.getMessage()
        if record.exc_info:
            msg="\n"+self.formatException(record.exc_info)

        line = (
            f"[{ts}] "
            f"{color}{level:<8}{self.RESET} "
            f"\033[90m{record.name:<30}{self.RESET} │ "
            f"{msg}"
            f"{extra_str}"
        )

        return line
    

'''SETUP LOGGER'''
def setup_logging(level:str="INFO")->None:
    """
    Configure the root logger.  Call this early in application startup
    (inside the lifespan context manager is ideal).

    Args:
        level: One of DEBUG / INFO / WARNING / ERROR / CRITICAL.
    """
    root=logging.getLogger()
    root.setLevel(getattr(logging,level.upper(),logging.INFO))


    #!remove any handlers added by uvicorn before we touch them
    root.handlers.clear()

    handler=logging.StreamHandler(sys.stdout)
    handler.setFormatter(ShelbyFormatter())
    root.addHandler(handler)

    #*silence noisy third-party loggers.
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").propagate = False


def get_logger(name:str)->logging.Logger:
    """
    Convenience wrapper so every module gets a named logger.
    """
    return logging.getLogger(name)