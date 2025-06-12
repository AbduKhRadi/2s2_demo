from pydantic import BaseModel, Field
from typing import List

class DetectionDocumentation(BaseModel):
    title: str = Field(..., description="Detection rule title")
    use_case: str = Field(..., description="What the detection is for")
    rationale: str = Field(..., description="Why this detection matters")
    coverage: str = Field(..., description="How the detection works technically")
    false_positives: List[str] = Field(..., description="Common causes for false alerts")
    references: List[str] = Field(..., description="External URLs or named references")
