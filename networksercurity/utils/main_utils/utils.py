import yaml
from networksercurity.Exception import custom_expection
from networksercurity.logging import logger
import os,sys
import numpy as np
import dill
import pickle
from sklearn.metrics import r2_score
from sklearn.model_selection import GridSearchCV


def read_yaml_file(file_path:str) -> dict:
    try:
        with open(file_path, 'rb') as yaml_file:
            return yaml.safe_load(yaml_file)
        
    except Exception as e:
        raise custom_expection(e,sys) from e     
    
    
def write_yaml_file(file_path:str,content:object,replace:bool = False) -> None:
    try:
        if replace:
            if os.path.exists(file_path):
                os.remove(file_path)
        os.makedirs(os.path.dirname(file_path),exist_ok=True)
        with open(file_path, "w") as file:
            yaml.dump(content,file)
    except Exception as e:
        raise custom_expection(e,sys)
            
            
def save_numpy_array(file_path:str,array:np.array):
    try:
        dir_path=os.path.dirname(file_path)
        os.makedirs(dir_path,exist_ok=True)
        with open(file_path,'wb') as file_obj:
            np.save(file_obj,array)
    except Exception as e:
        raise custom_expection(e,sys) from e
    
def save_object(file_path:str,obj:object)-> None:
    try:
        logger.info("entered the save_object method of main utils class")
        os.makedirs(os.path.dirname(file_path),exist_ok=True)
        with open(file_path,'wb') as file_obj:
            pickle.dump(obj,file_obj)
        logger.info("exited the save_object method of main utils class")
    except Exception as e:
        raise custom_expection(e,sys) from e                                
            
                    
def load_object(file_path:str,)->object:
    try:
        if not os.path.exists(file_path):
            raise Exception(f"the file :{file_path} is not exists")
        
        with open(file_path,"rb") as file_obj:
            print(file_obj)
            return pickle.load(file_obj)
        
    except Exception as e:
        raise custom_expection(e,sys) from e    
                        
                    
def load_numpy_array_data(file_path:str)->np.array:
    
    try:
        with open(file_path,'rb') as file_obj:
            return np.load(file_obj)
    except Exception as e:
        raise custom_expection (e,sys) from e
    
    
def evalute_model(X_train, y_train, X_test, y_test, models, param):
    try:
        report = {}

        for i in range(len(list(models))):
            model_name = list(models.keys())[i]  # Get the model name
            model = models[model_name]  # Get the actual model instance
            para = param[model_name]  # Get the hyperparameter grid for the model

            # Perform hyperparameter tuning
            gs = GridSearchCV(model, para, cv=3)
            gs.fit(X_train, y_train)

            # Set the best parameters and fit the model
            model.set_params(**gs.best_params_)
            model.fit(X_train, y_train)

            # Evaluate the model on train and test data
            y_train_pred = model.predict(X_train)
            y_test_pred = model.predict(X_test)

            train_model_score = r2_score(y_train, y_train_pred)
            test_model_score = r2_score(y_test, y_test_pred)

            # Store the test score in the report
            report[model_name] = test_model_score

        return report
    except Exception as e:
        raise custom_expection(e, sys)
