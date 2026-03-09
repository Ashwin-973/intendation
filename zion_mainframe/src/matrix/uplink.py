
import asyncio
from colorama import init, Fore, Back, Style

init(autoreset=True)

async def extract_operator_signature(name:str,filesize:int)->int:
    try:
        print(f"[TANK] extracting signature of {name}....")
        if name=="Morpheus":
            raise ConnectionError(Back.red+"Agent Smith intercepted Morpheus' signal , sever the line immediately to avoid him tracking back zion's ship")
        await asyncio.sleep(filesize/100)
        print(Fore.GREEN+f"[TANK] finished extracting signature of {name}!!")
    except Exception as e:
        raise e
