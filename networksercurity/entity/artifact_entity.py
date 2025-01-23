from dataclasses import dataclass

@dataclass
class DataIngestionArtifact:
    trained_file_path:set
    test_file_path:str
    
    