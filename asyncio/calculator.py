import asyncio
import sys
from aioconsole import ainput


def singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return getinstance


@singleton
class Calc:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.result = 0
        self.changed = False
        self.last_operation = ""

    async def set_operation(self, operation: str):
        print(f"Setting operation: {operation}")
        if operation == "+":
            self.result = self.x + self.y
            self.changed = True
        elif operation == "-":
            self.result = self.x - self.y
            self.changed = True
        elif operation == "*":
            self.result = self.x * self.y
            self.changed = True
        elif operation == "/":
            self.result = self.x / self.y
            self.changed = True
        self.last_operation = operation


async def get_operation():
    print("Reading operations")
    cc = Calc()
    while True:
        operation: str = await ainput("command >>> ")
        if operation.strip() == "":
            break
        print(f"Current operation: '{operation}'")
        await cc.set_operation(operation)


async def show():
    print("Start show")
    cc = Calc()
    while True:
        if cc.changed:
            print(f"\nResult of operation '{cc.last_operation}' is {cc.result}")
            cc.changed = False
        await asyncio.sleep(0.1)


async def main():
    cc = Calc()
    cc.x = int(input("Set value x:"))
    cc.y = int(input("Set value y:"))
    task1 = asyncio.create_task(get_operation())
    task2 = asyncio.create_task(show())
    await task1
    await task2


asyncio.run(main())
