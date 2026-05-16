from fastapi import BackgroundTasks, FastAPI
from app.models import ScrapedOffer
from app.services.matching import process_offer

app = FastAPI(title="Offer Hunter API", version="0.0.1", description="API para ingestão de ofertas.")

@app.get("/health")
async def health_check():
    return {"status": "online", "message": "Motor de ofertas pronto!"}

@app.post("/api/v1/ingest/offer", status_code=202)
async def ingest_offer(offer: ScrapedOffer, background_tasks: BackgroundTasks):
    background_tasks.add_task(process_offer, offer)
    
    return {
        "status": "accepted",
        "message": f"Processando oferta {offer.external_id} da {offer.source}."
    }