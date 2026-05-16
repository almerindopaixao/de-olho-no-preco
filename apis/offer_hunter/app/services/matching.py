import os
import httpx
from datetime import datetime, timezone
from apis.offer_hunter_api.app.models import ScrapedOffer
from apis.offer_hunter_api.app.database import get_db

N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")

async def process_offer(offer: ScrapedOffer):
    db = await get_db()
    

    utc_now = datetime.now(timezone.utc)
    new_offer = {
        "source": offer.source,
        "title": offer.title,
        "affiliate_url": offer.affiliate_url,
        "current_price": offer.current_price,
        "image_url": offer.image_url,
        "captured_at": utc_now.isoformat()
    }
    
    await db.offers.update_one(
        {"source": offer.source, "external_id": offer.external_id},
        {"$set": new_offer},
        upsert=True
    )
    
    current_month = utc_now.strftime("%Y-%m")
    
    new_price_entry = {
        "date": utc_now.isoformat(),
        "price": offer.current_price
    }

    await db.price_history.update_one(
        {"external_id": offer.external_id, "period": current_month},
        {
            "$push": {"prices": new_price_entry},
            "$inc": {
                "metrics.price.count": 1, 
                "metrics.price.total": offer.current_price
            },
            "$min": {"metrics.price.min": offer.current_price},
            "$max": {"metrics.price.max": offer.current_price},
        },
        upsert=True
    )
    
    print(f"✅ Salvo no banco: {offer.title} - R$ {offer.current_price}")

    history_doc = await db.price_history.find_one({"external_id": offer.external_id, "period": current_month})
    
    if history_doc and "prices" in history_doc:
        avg_price = history_doc["metrics"]["price"]["total"] / history_doc["metrics"]["price"]["count"]
    
        # Se o preço atual for pelo menos 15% menor ou igual que a média histórica
        is_super_offer = offer.current_price <= (avg_price * 0.85)
        
        if is_super_offer:
            print(f"🚨 SUPER OFERTA DETECTADA! Média: {avg_price:.2f} | Atual: {offer.current_price:.2f}")
            await notify_n8n(offer, avg_price)

async def notify_n8n(offer: ScrapedOffer, avg_price: float):
    payload = {
        "title": offer.title,
        "source": offer.source,
        "current_price": offer.current_price,
        "historical_avg": round(avg_price, 2),
        "affiliate_url": offer.affiliate_url,
        "image_url": offer.image_url
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(N8N_WEBHOOK_URL, json=payload)
            print(f"📨 Enviado para o n8n com status: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Erro ao avisar o n8n: {e}")