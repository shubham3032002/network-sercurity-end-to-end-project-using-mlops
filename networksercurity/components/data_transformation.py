import sys
import os
from networksercurity.logging import logger
import numpy as np
import pandas as pd
from sklearn.impute import KNNImputer
from sklearn.pipeline import Pipeline
from networksercurity.Exception import custom_expection
from networksercurity.constant.training_pipeline import TARGET_COLUMN
from networksercurity.constant.training_pipeline import DATA_TRANSFORMATION_IMPUTER_PARAMS
from networksercurity.entity.artifact_entity import (DataTransformationArtifact,DataValidationArtifact)
from networksercurity.entity.config_entity import DataTransformationConfig
from networksercurity.utils.main_utils.utils import save_numpy_array,save_object


class DataTransformation:
    def __init__(self,data_validation_artifact:DataValidationArtifact,
                 data_transformation_config:DataTransformationConfig):
        try:
            self.data_validation_artifact=data_validation_artifact
            self.data_transformation_config=data_transformation_config
            
            
        except Exception as e:
            raise custom_expection(e,sys)
        
        
    @staticmethod
    def read_data(file_path) -> pd.DataFrame:
        try:
            df=pd.read_csv(file_path)
            return df 
        except Exception as e:
            raise custom_expection(e,sys) 
        
    def get_data_transformer_object(cls) -> Pipeline:
        try:
            logger.info("initial the knn imputer")
            imputer:KNNImputer=KNNImputer(**DATA_TRANSFORMATION_IMPUTER_PARAMS)
            processor:Pipeline=Pipeline([("imputer",imputer)])
            
            return processor
        except Exception  as e:
            raise custom_expection(e,sys)
        
    def initiate_data_transformation(self)->DataTransformationArtifact    :
        logger.info('entered initial_data_transformation method of datatransformation class')
        try:
            logger.info("starting data transformation")
            train_df=DataTransformation.read_data(self.data_validation_artifact.valid_train_file_path)
            test_df=DataTransformation.read_data(self.data_validation_artifact.valid_test_file_path)
            
            #training dataframe
            input_feature_train_df=train_df.drop(columns=[TARGET_COLUMN],axis=1)
            target_feature_train_df=train_df[TARGET_COLUMN]
            target_feature_train_df=target_feature_train_df.replace(-1,0)
            
            #testing dataframe
            input_feature_test_df=test_df.drop(columns=[TARGET_COLUMN],axis=1)
            target_feature_test_df=test_df[TARGET_COLUMN]
            target_feature_test_df=target_feature_test_df.replace(-1,0)
            
            preprocessor=self.get_data_transformer_object()
            preprocessor_object=preprocessor.fit(input_feature_train_df)
            transformed_input_train_feature=preprocessor.transform(input_feature_train_df)
            transformed_input_test_feature=preprocessor.transform(input_feature_test_df)
            
            
            train_arr=np.c_[transformed_input_train_feature,np.array(target_feature_train_df)]
            test_arr=np.c_[transformed_input_test_feature,np.array(target_feature_test_df)]
            
            #save numpy array data
            save_numpy_array(self.data_transformation_config.transformed_train_file_path,array=train_arr,)
            save_numpy_array(self.data_transformation_config.transformed_test_file_path,array=test_arr,)
            save_object(self.data_transformation_config.transformed_object_file_path,preprocessor_object,)
            
            save_object("final_model/preprocessor.pkl",preprocessor_object,)
            
            
            #preparing atifact
            data_transformation_artifact=DataTransformationArtifact(
                transformed_object_file_path=self.data_transformation_config.transformed_object_file_path,
                transformed_train_file_path=self.data_transformation_config.transformed_train_file_path,
                transformed_test_file_path=self.data_transformation_config.transformed_test_file_path
                
            )
            
            return data_transformation_artifact
            
            
        except Exception as e:
            raise custom_expection(e,sys)