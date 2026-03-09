from src.matrix import extract_operator_signature

import asyncio
from colorama import init, Fore, Back, Style
import traceback
import logging


init(autoreset=True) #initialize colorama

async def run_uplink():
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(extract_operator_signature("Trinity",300))
            tg.create_task(extract_operator_signature("Neo",500))
            # tg.create_task(extract_operator_signature("Morpheus",7000))
            tg.create_task(extract_operator_signature("Mouse",200))
    except ExceptionGroup as eg:
        print(Fore.RED + f"an exception occured in one or more of the extract operation")
        raise eg




if __name__=="__main__":
    try:
        asyncio.run(run_uplink())
    except Exception as e:
        traceback.print_exc()
        # Capture the traceback as a string for logging
        error_msg = traceback.format_exc()
        logging.error("Detailed error info:\n%s", error_msg) 


'''I don't like the idea that I'm not in control of my life --Neo'''
