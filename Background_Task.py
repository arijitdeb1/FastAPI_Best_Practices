from fastapi import FastAPI, BackgroundTasks

app = FastAPI()


def process_item(item: dict):
    # Time-consuming operation here
    pass


@app.post("/items")
async def create_item(item: dict, background_tasks: BackgroundTasks):
    background_tasks.add_task(process_item, item)
    return {"message": "Item received, processing in background"}
