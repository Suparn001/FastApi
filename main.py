from fastapi import FastAPI,Path, HTTPException,Query
import json
app= FastAPI()

def load_data():
    with open('patients.json','r') as f:
        data=json.load(f)

    return data

@app.get("/") # @ is decorator
def hello():
    return {'message':'Patient Managment API'}  # this is dictionary

@app.get("/about")
def about():
    return {'message':'A fully functional API to manage your patient records'}

@app.get("/view")
def view():
    data=load_data()
    return data


@app.get("/patient/{patiend_id}")
def getSinglePateint(patiend_id: str=Path(...,description="ID of the Patient in DB", example="P001")):
    # load all the patients
    data = load_data()

    if patiend_id in data:
        return data[patiend_id]
    # else:
    #     return {
    #         'error':'patient not found',
    #         'message':'patient not found'}
    raise HTTPException (status_code=404,detail=f"Patient with id {patiend_id} not found")



# Query Parameter
@app.get('/sort')
def sort_patients(sort_by:str=Query(...,description="Sort on the basis of height, weight,bmi"),order:str=Query('asc',description="Sort in asceding or descending order, be default it is asc")):
    valid_fields=['height','weight','bmi']
    if sort_by not in valid_fields:
        raise HTTPException(status_code=400,detail=f"Invalid fields select from {valid_fields}")
    

    if order not in ['asc','desc']:
        raise HTTPException(status_code=400,detail="Invalid order select between asc and desc")
    
    data = load_data()
    sort_order= True if order=="desc" else False
    sorted_data = sorted(data.values(),key=lambda x: x.get(sort_by,0), reverse=sort_order)

    return sorted_data