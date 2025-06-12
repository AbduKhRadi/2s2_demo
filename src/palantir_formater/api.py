from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
from typing import List
import yaml

from .types import DetectionDocumentation, read_detection_yaml

app = FastAPI(
    title="Detection Documentation API",
    description="API for managing and retrieving detection documentation",
    version="1.0.0"
)

@app.get("/detection/{detection_id}", response_model=DetectionDocumentation)
async def get_detection(detection_id: str):
    """
    Retrieve detection documentation by ID.
    
    Args:
        detection_id: The ID of the detection (filename without extension)
        
    Returns:
        DetectionDocumentation: The parsed detection documentation
        
    Raises:
        HTTPException: If the detection file is not found or invalid
    """
    try:
        # Assuming detections are stored in a 'detections' directory
        file_path = Path("detections") / f"{detection_id}.yaml"
        detection = read_detection_yaml(file_path)
        return detection
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Detection {detection_id} not found")
    except yaml.YAMLError as e:
        raise HTTPException(status_code=400, detail=f"Invalid YAML format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing detection: {str(e)}")

@app.get("/detections", response_model=List[str])
async def list_detections():
    """
    List all available detection IDs.
    
    Returns:
        List[str]: List of detection IDs (filenames without extension)
    """
    try:
        detections_dir = Path("detections")
        if not detections_dir.exists():
            return []
        
        # Get all .yaml files and return their names without extension
        return [f.stem for f in detections_dir.glob("*.yaml")]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing detections: {str(e)}")

# Optional: Add a health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"} 