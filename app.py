import os
import sys
import pandas as pd
import certifi
from networksercurity.Exception import custom_expection
from dotenv import load_dotenv
from fastapi import FastAPI, Response
from networksercurity.pipeline.training_pipeline import Trainingpipeline
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
from uvicorn import run as app_run
from fastapi import FastAPI, File, UploadFile,Request
import pymongo
from networksercurity.utils.ml_utils.model.estimator import NetworkModel

from networksercurity.utils.main_utils.utils import load_object
# Loading environment variables
load_dotenv()

mongo_db_url = os.getenv('MONGODB_URL')
client = pymongo.MongoClient(mongo_db_url, tlsCAFile=certifi.where())

# Initialize FastAPI app
app = FastAPI()

# CORS Middleware
origins = ['*']
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="./templetes")
@app.get("/", tags=["authentication"])
async def index():
    return RedirectResponse(url="/docs")

@app.get("/train")
async def train_route():
    try:
        # Initialize the training pipeline
        train_pipeline = Trainingpipeline()
        model_train_artifact = train_pipeline.run_pipeline()  # Run the pipeline
        return Response(f"Training is successful. Model artifact: {model_train_artifact}")
    except Exception as e:
        return Response(f"An error occurred: {str(e)}", status_code=500)
    
    
@app.post("/predict")
async def predict_route(request: Request,file: UploadFile = File(...)):
    try:
        df=pd.read_csv(file.file)
        #print(df)
        preprocesor=load_object("final_model/preprocessor.pkl")
        final_model=load_object("final_model/model.pkl")
        network_model = NetworkModel(preprocessor=preprocesor,model=final_model)
        print(df.iloc[0])
        y_pred = network_model.predict(df)
        print(y_pred)
        df['predicted_column'] = y_pred
        print(df['predicted_column'])
        #df['predicted_column'].replace(-1, 0)
        #return df.to_json()
        df.to_csv('prediction_output/output.csv')
        table_html = df.to_html(classes='table table-striped')
        #print(table_html)
        return templates.TemplateResponse("table.html", {"request": request, "table": table_html})
        
    except Exception as e:
            raise custom_expection(e,sys)
       

if __name__ == "__main__":
    app_run(app, host="0.0.0.0", port=8000)
