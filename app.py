from fastapi import FastAPI
app = FastAPI()


@app.get("/")
async def index():
    return "Hello, I'm the index page!"


@app.get("/say/{something}")
async def say_something(something):
    print(something)
