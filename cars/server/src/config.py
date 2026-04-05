"""
uses environment variables with sensible defaults.
in a real project you'd pull in `pydantic-settings` for .env file support —
kept as stdlib here to minimise dependencies.
"""
from __future__ import annotations

import os

class Settings:
    """
     central config object.  All tuneable knobs live here so you never
     have magic strings scattered across the codebase.
     """
    
    '''APPLICATION'''
    app_name:str=os.getenv("APP_NAME","Shelby American")
    app_version:str=os.getenv("APP_VERSION","1.0.1")
    debug:bool=os.getenv("DEBUG","false").lower()=="true"

    '''SERVER'''
    host:str=os.getenv("HOST", "127.0.0.1")
    port:int=int(os.getenv("PORT",8000))
    reload:bool=os.getenv("RELOAD","false").lower()=="true"

    '''LOGGING'''
    log_level:str=os.getenv("LOG_LEVEL", "DEBUG" if debug else "INFO")

    '''DEFAULT PAGINATION'''
    default_page_size:int=int(os.getenv("DEFAULT_PAGE_SIZE", "20"))
    max_page_size:int=int(os.getenv("MAX_PAGE_SIZE", "100"))

    '''RATE LIMITING'''
    rate_limit_per_minute:int =int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))

    def __repr__(self) -> str:
        return (
            f"Settings("
            f"app_name={self.app_name!r}, "
            f"version={self.app_version!r}, "
            f"debug={self.debug}, "
            f"log_level={self.log_level!r})"
        )


settings=Settings()


