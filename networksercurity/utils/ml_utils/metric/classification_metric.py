from networksercurity.entity.artifact_entity import ClassificationMetricArtifact
from networksercurity.Exception import custom_expection
from sklearn.metrics import f1_score,precision_score,recall_score
import sys

def get_classification_score(y_true,y_pred):
    try:
        model_f1_score=f1_score(y_true,y_pred)
        model_recall_score=recall_score(y_true,y_pred)
        model_precision_score=precision_score(y_true,y_pred)
        
        classification_metrics=ClassificationMetricArtifact(f1_score=model_f1_score,
                                                            recall_score=model_f1_score,
                                                            precision_score=model_f1_score,
                                                            )
        return classification_metrics
    
    except Exception as e:
        raise custom_expection(e,sys)