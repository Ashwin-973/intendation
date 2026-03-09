from src.matrix import extract_operator_signature

import asyncio


async def run_uplink():
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(extract_operator_signature("Trinity",3000))
            tg.create_task(extract_operator_signature("Neo",5000))
            tg.create_task(extract_operator_signature("Morpheus",7000))
            tg.create_task(extract_operator_signature("Mouse",2000))
    except ExceptionGroup as eg:
        print(f"an exception occured in one or more of the extract operation")
        raise eg




if __name__=="__main__":
    try:
        asyncio.run()
    except Exception as e:
        print(f"Error at Main Program : {e}")


'''I don't like the idea that I'm not in control of my life --Neo'''
