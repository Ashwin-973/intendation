
import asyncio


def extract_operator_signature(name:str,filesize:int)->int:
    print(f"[TANK] extracting signature of {name}....")
    if name=="Morpheus":
        raise ConnectionError("Agent Smith intercepted Morpheus' signal , sever the line immediately to avoid him tracking back zion's ship")
    asyncio.sleep(filesize/100)
    print(f"[TANK] finished extracting signature of {name}!!")
