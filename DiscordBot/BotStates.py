import asyncio
vars = {
    "kill": False,
    "run": False,
    "set_task": [False,"",""],
    "exit": False
}
_callbacks = []
async def change_variable(key, value):
    vars[key] = value
    for cb in _callbacks:
        asyncio.create_task(_run_callback(cb))

async def _run_callback(cb):
    try:
        result = cb()
        if asyncio.iscoroutine(result):
            await result
    except Exception as e:
        print("Callback error:", e)



def add_callback(callback):
    _callbacks.append(callback)