from fastapi import FastAPI,Path, HTTPException,Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel,Field,computed_field
from typing import Annotated,Literal,Optional
import json
app= FastAPI()


class Patient(BaseModel):
    id: Annotated[
        str,
        Field(..., description="Id of patient", examples=["P001"])
    ]

    name: Annotated[
        str,
        Field(..., description="Name of the patient", examples=["Ashish"])
    ]

    city: Annotated[
        str,
        Field(..., description="City where the patient is living", examples=["Gurgaon"])
    ]

    age: Annotated[
        int,
        Field(..., gt=0, lt=120, description="Age of the patient")
    ]

    gender: Annotated[
        Literal["male", "female", "other"],
        Field(description="Gender of the patient")
    ]

    height: Annotated[
        float,
        Field(..., gt=0, description="Height of the patient in meters")
    ]

    weight: Annotated[
        float,
        Field(..., gt=0, description="Weight of the patient in kg")
    ]

    @computed_field
    @property
    def bmi(self) -> float:
        return round(self.weight / (self.height ** 2), 2)

    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi < 18.5:
            return "UnderWeight"
        elif self.bmi < 25:
            return "Normal"
        elif self.bmi < 30:
            return "OverWeight"
        else:
            return "Obese"

def load_data():
    with open('patients.json','r') as f:
        data=json.load(f)

    return data

def save_data(data):
    with open('patients.json','w') as f:
        json.dump(data,f)

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

@app.post('/create')
def create_patient(patient:Patient):
    # load exisitng data
    data = load_data()

    # check if patient already exists

    if patient.id in data:
        raise HTTPException(status_code=400,detail=f'Patient with this {patient.id} already exist')


    # new ptient add to database
    data[patient.id] = patient.model_dump(exclude=['id'])

    #save into json file
    save_data(data)

    return JSONResponse(status_code=201,content={'message':'Patient created successfully'})

class PatientUpdate(BaseModel):
    name: Annotated[
        Optional[str],
        Field(default=None)
    ]

    city: Annotated[
        Optional[str],
        Field(default=None)
    ]

    age: Annotated[
        Optional[int],
        Field(default=None)
    ]

    gender: Annotated[
        Optional[Literal["male", "female", "other"]],
        Field(default=None)
    ]

    height: Annotated[
        Optional[float],
        Field(default=None)
    ]

    weight: Annotated[
        Optional[float],
        Field(default=None)
    ]

    @computed_field
    @property
    def bmi(self) -> float:
        if self.height is None or self.weight is None:
            return None
        return round(self.weight / (self.height ** 2), 2)

    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi is None:
            return None
        if self.bmi < 18.5:
            return "UnderWeight"
        elif self.bmi < 25:
            return "Normal"
        elif self.bmi < 30:
            return "OverWeight"
        else:
            return "Obese"
        


@app.put('/edit/{patient_id}')
def update_patient(patient_id:str, patient_update:PatientUpdate):
    data  = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient id is not correct")
    
    exisitng_patient_info=data[patient_id]
    print(exisitng_patient_info )
    updated_patient_info = patient_update.model_dump(exclude_unset=True) #exclude_unset 
    for key,value in updated_patient_info.items():
        exisitng_patient_info[key] = value

    exisitng_patient_info['id'] = patient_id
    patient_pydantic_object=Patient(**exisitng_patient_info)
    exisitng_patient_info=patient_pydantic_object.model_dump(exclude='id')

    # add this dic to data
    data[patient_id] = exisitng_patient_info

    save_data(data)


    return JSONResponse(status_code=200,content={'message':'Patient updated'})


@app.delete('/delete/{patient_id}')
def delete_patient(patient_id:str):
    data =load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    del data[patient_id]
    save_data(data)

    return JSONResponse(status_code=200, content={'message':'patient deleted'})
