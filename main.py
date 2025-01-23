from networksercurity.logging import logger
from networksercurity.Exception import custom_expection
from networksercurity.components.data_ingestion import DataIngestion
import sys

from networksercurity.entity.config_entity import DataIngestionConfig
from networksercurity.entity.config_entity import TrainingPipelineConfig

if __name__ =="__main__":
    try:
       training_pipeline_config=TrainingPipelineConfig()
       dataingestion_config=DataIngestionConfig(training_pipeline_config)
       dataingestion=DataIngestion(dataingestion_config)
       logger.info("initiate the data ingestion")
       dataingestionartifact=dataingestion.initiate_data_ingestion()
       print(dataingestionartifact)
        
    except Exception as e:
        raise custom_expection(e,sys)    
    