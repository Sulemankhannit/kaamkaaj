from fastapi import FastAPI
from pydantic import BaseModel
class Quest_Creat(BaseModel):
    name:str
    description:str|None=None
    xp_reward:int


app=FastAPI()
@app.get("/")
async def welcome_to_questlog():
    return{
       "message":"Welcome to tavern,Adventurer",
       "status":"server is correctly runnning."
    }

@app.get("/quests/{quest_id}")
async def get_quest(quest_id:int):
    return {
        "quest_id": quest_id,
        "quest_name": f"Defeat the Goblin King (ID: {quest_id})",
        "xp_reward": 500,
        "status": "Incomplete"
    }

@app.get("/quests/")
async def list_quests(skip:int,limit:int):
    return {
        "message":f"Fetching quests from the database...",
        "skipping_first":skip,
        "total_to_return":limit
    }


@app.post("/quests/")
async def create_quest(quest:Quest_Creat):
    print("Server log:quest is being created")
    return{
        "message":f"your quest named:{quest.name} and worth {quest.xp_reward}xp is created!",
        "quest_data":quest
    }
    

    


    