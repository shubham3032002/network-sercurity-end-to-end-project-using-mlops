from networksercurity.logging import logger
from networksercurity.Exception import custom_expection
from networksercurity.components.data_ingestion import DataIngestion
from networksercurity.components.data_validation import DataValidation
from networksercurity.components.data_transformation import DataTransformation
from networksercurity.components.model_trainer import ModelTrainer
from networksercurity.entity.config_entity import (
    DataIngestionConfig,
    DataValidationConfig,
    DataTransformationConfig,
    ModelTrainerConfig,
    TrainingPipelineConfig,
)
import sys

if __name__ == "__main__":
    try:
        # Initialize Training Pipeline Configuration
        training_pipeline_config = TrainingPipelineConfig()

        # Step 1: Data Ingestion
        logger.info("Initializing Data Ingestion...")
        data_ingestion_config = DataIngestionConfig(training_pipeline_config)
        data_ingestion = DataIngestion(data_ingestion_config)
        data_ingestion_artifact = data_ingestion.initiate_data_ingestion()
        logger.info("Data Ingestion completed successfully.")
        print(data_ingestion_artifact)

        # Step 2: Data Validation
        logger.info("Initializing Data Validation...")
        data_validation_config = DataValidationConfig(training_pipeline_config)
        data_validation = DataValidation(data_ingestion_artifact, data_validation_config)
        data_validation_artifact = data_validation.initiate_data_validation()
        logger.info("Data Validation completed successfully.")
        print(data_validation_artifact)

        # Step 3: Data Transformation
        logger.info("Initializing Data Transformation...")
        data_transformation_config = DataTransformationConfig(training_pipeline_config)
        data_transformation = DataTransformation(data_validation_artifact, data_transformation_config)
        data_transformation_artifact = data_transformation.initiate_data_transformation()
        logger.info("Data Transformation completed successfully.")
        print(data_transformation_artifact)

        # Step 4: Model Training
        logger.info("Initializing Model Training...")
        model_trainer_config = ModelTrainerConfig(training_pipeline_config)
        model_trainer = ModelTrainer(
        model_trainer_config=model_trainer_config,  # Correct argument name
        data_transformation_artifact=data_transformation_artifact,
        )
        model_trainer_artifact = model_trainer.initiate_model_trainer()
        logger.info("Model Training completed successfully.")
        print(model_trainer_artifact)

    except Exception as e:
        logger.error("An error occurred during the pipeline execution.", exc_info=True)
        raise custom_expection(e, sys)

