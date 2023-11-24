# Imports para el fastapi
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

# Imports para poder acceder al API de most_wanted del FBI
import requests
import json

# Obtenemos los datos de la API
response = requests.get('https://api.fbi.gov/wanted/v1/list', params={"pageSize": 50,})
data = json.loads(response.content)

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.mount("/", StaticFiles(directory="static", html=True), name="static")

################################ ALMACENAMOS LOS DATOS QUE NOS INTERESAN EN UN DICCIONARIO #############################################

buscados: list = []
for suspect in data['items']:
    buscados.append(
        {
            'sex': suspect['sex'],
            'nationality': suspect['nationality'],
            'age_min': suspect['age_min'],
            'age_max': suspect['age_max'],
            'scars_and_marks': suspect['scars_and_marks']
        }
    )
    
########################################################################################################################################

@app.get("/", response_class=HTMLResponse)
def get_root():
    return open("static/index.html", "r").read()

@app.get("/age_range/{min_age}")
def age_range(min_age: int):
    min_age = int(min_age)
    buscados_age: list = []
    
    for suspect in buscados:
        if suspect['age_min'] is not None:
            if suspect['age_min'] >= min_age:
                buscados_age.append(suspect)
                
    return buscados_age
        
@app.get("/no_nationality_known")
def get_no_nationality():
    count_none: int = 0
    for suspect in buscados:
        if suspect['nationality'] in [None, "Unknown"]:
            count_none += 1

    return (count_none / len(data['items'])) * 100 # Porcentaje de Nones en el campo Nacionalidad

@app.get("/nationality_known")
def get_no_nationality():
    suspects_with_known_nationality = []
    for suspect in buscados:
        if suspect['nationality'] not in [None, "Unknown"]:
            suspects_with_known_nationality.append(suspect)

    return suspects_with_known_nationality

@app.get("/nationality/{nationality}")
def getNationality(nationality):
    suspects_with_nationality = []
    for suspect in buscados:
        if suspect['nationality'] is not None:
            if suspect['nationality'].lower() == nationality.lower():
                suspects_with_nationality.append(suspect)
                    
    return suspects_with_nationality

@app.get("/males")
def getMales():
    males = []
    for suspect in buscados:
        if suspect['sex'] == 'Male':
            males.append(suspect)

    return males

@app.get("/females")
def getFemales():
    females = []
    for suspect in buscados:
        if suspect['sex'] == 'Female':
            females.append(suspect)

    return females

@app.get("/scars")
def getScars():
    scars = []
    for suspect in buscados:
        if suspect['scars_and_marks'] != None:
            scars.append(suspect)

    return scars
