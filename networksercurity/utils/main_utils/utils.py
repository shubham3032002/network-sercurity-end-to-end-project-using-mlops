import yaml
from networksercurity.Exception import custom_expection
from networksercurity.logging import logger
import os,sys
import numpy as np
import dill
import pickle



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
            
                    