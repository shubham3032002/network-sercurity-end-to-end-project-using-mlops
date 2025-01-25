from networksercurity.logging import logger
from networksercurity.Exception import custom_expection
from networksercurity.components.data_ingestion import DataIngestion
import sys
from networksercurity.components.data_validation import DataValidation
from networksercurity.entity.config_entity import DataIngestionConfig,DataValidationConfig,DataTransformationConfig
from networksercurity.entity.config_entity import TrainingPipelineConfig
from networksercurity.components.data_transformation import DataTransformation

if __name__ =="__main__":
    try:
       training_pipeline_config=TrainingPipelineConfig()
       
       dataingestion_config=DataIngestionConfig(training_pipeline_config)
       dataingestion=DataIngestion(dataingestion_config)
       logger.info("initiate the data ingestion")
       dataingestionartifact=dataingestion.initiate_data_ingestion()
       print(dataingestionartifact)
       logger.info("data initiation completed")
       
       
       data_validation_config = DataValidationConfig(training_pipeline_config)
       data_validation = DataValidation(dataingestionartifact, data_validation_config)
       logger.info("initiate the data validation")
       data_validation_artifact=data_validation.initiate_data_validation()
       logger.info("data validation completed")
       print(data_validation_artifact)
       
       logger.info("data tranformation started")
       data_transformation_config=DataTransformationConfig(training_pipeline_config)
       data_transformation=DataTransformation(data_validation_artifact,data_transformation_config)
       data_transformation_artifact=data_transformation.initiate_data_transformation()
       logger.info("data tranformation competed")
       print(data_transformation_artifact)
       
       
        
    except Exception as e:
        raise custom_expection(e,sys)    
    