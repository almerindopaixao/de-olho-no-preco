import asyncio
import httpx
from client import ShopeeAffiliateAPI

# URL da nossa API principal (O seu sistema FastAPI)
INGESTION_API_URL = "http://localhost:8000/api/v1/ingest/offer"

# Chaves fictícias por enquanto (Quando aprovar, coloque no arquivo .env)
APP_ID = "APP_ID_FALSO_123"
APP_SECRET = "SECRET_FALSO_456"

async def extract_and_ingest(keyword: str):
    # Instancia o cliente com use_mock=True
    # Quando for pra produção, é só mudar para use_mock=False!
    shopee = ShopeeAffiliateAPI(app_id=APP_ID, app_secret=APP_SECRET, use_mock=True)
    
    try:
        response_data = await shopee.get_product_offers(keyword=keyword, limit=5)
        
        # Navega pelo JSON da resposta GraphQL
        nodes = response_data.get("productOfferV2", {}).get("nodes", [])
        
        if not nodes:
            print("❌ Nenhum produto retornado ou erro na query.")
            return

        async with httpx.AsyncClient() as client:
            for item in nodes:
                # Prepara o objeto exatamente como nossa API Hunter exige
                payload = {
                    "source": "shopee",
                    "external_id": item.get("item_id"),
                    "title": item.get("item_name"),
                    "current_price": float(item.get("item_price")),
                    "affiliate_url": item.get("offer_link"),
                    "image_url": item.get("image_url")
                }
                
                # Envia para o nosso banco de dados (A Fase 3 do MVP)
                await send_to_hunter_api(client, payload)

    except Exception as e:
        print(f"⚠️ Erro crítico na execução: {e}")

async def send_to_hunter_api(client: httpx.AsyncClient, payload: dict):
    try:
        response = await client.post(INGESTION_API_URL, json=payload)
        if response.status_code == 202:
            print(f"✅ Oferta Ingerida: R$ {payload['current_price']} -> {payload['title'][:30]}...")
    except Exception as e:
        print(f"⚠️ Erro ao enviar para Hunter API: {e}")

if __name__ == "__main__":
    asyncio.run(extract_and_ingest("Notebook Gamer"))