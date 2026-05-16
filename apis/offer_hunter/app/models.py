from pydantic import BaseModel, Field
from typing import Optional

class ScrapedOffer(BaseModel):
    source: str = Field(..., description="amazon, mercado_livre, shopee")
    external_id: str
    title: str
    current_price: float
    affiliate_url: str
    gtin_ean: Optional[str] = None
    image_url: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "source": "amazon",
                    "external_id": "B0BYXXXX123",
                    "title": "Smartphone Samsung Galaxy S23 256GB",
                    "current_price": 4000.00,
                    "affiliate_url": "https://amzn.to/exemplo123",
                    "image_url": "https://m.media-amazon.com/images/I/exemplo.jpg"
                }
            ]
        }
    }