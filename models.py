from pydantic import BaseModel
from typing import Optional


class Trial(BaseModel):
    trial_id: str
    crop: str
    product: str
    country: str
    year: Optional[int] = None
    trial_type: str

    treatment_yield_kg_ha: Optional[float] = None
    control_yield_kg_ha: Optional[float] = None

    source: str
    source_type: str
    notes: Optional[str] = None