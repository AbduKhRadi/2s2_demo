from pydantic import BaseModel, Field
from typing import List
import yaml
from pathlib import Path

class DetectionDocumentation(BaseModel):
    title: str = Field(..., description="Detection rule title")
    use_case: str = Field(..., description="What the detection is for")
    rationale: str = Field(..., description="Why this detection matters")
    coverage: str = Field(..., description="How the detection works technically")
    false_positives: List[str] = Field(..., description="Common causes for false alerts")
    references: List[str] = Field(..., description="External URLs or named references")

def read_detection_yaml(file_path: str | Path) -> DetectionDocumentation:
    """
    Read a YAML file and convert it to a DetectionDocumentation model.
    
    Args:
        file_path: Path to the YAML file
        
    Returns:
        DetectionDocumentation: Parsed detection documentation
        
    Raises:
        FileNotFoundError: If the YAML file doesn't exist
        yaml.YAMLError: If the YAML file is malformed
        ValidationError: If the YAML content doesn't match the model schema
    """
    with open(file_path, 'r') as f:
        yaml_content = yaml.safe_load(f)
    
    return DetectionDocumentation(**yaml_content)
