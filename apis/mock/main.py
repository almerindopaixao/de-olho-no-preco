from fastapi import FastAPI, Request
import uvicorn
import random

app = FastAPI(title="Shopee Affiliate API Mock - Strict Mode")

@app.post("/open_api/v2/affiliate/product_offer/list")
async def mock_product_offer(request: Request):
    """
    Simula a resposta EXATA da API GraphQL de Afiliados da Shopee.
    """
    # Lê os cabeçalhos para fingir que validamos a assinatura
    auth_header = request.headers.get("Authorization")
    print(f"🔐 Cabeçalho de Auth Recebido: {auth_header}")
    
    # Lê o corpo da requisição (a query GraphQL que nosso cliente mandou)
    body = await request.json()
    variables = body.get("variables", {})
    
    # Extrai a palavra-chave das variáveis de forma limpa
    keyword = variables.get("keyword", "Produto")
    mock_nodes = []
    for i in range(5): # Simula 5 resultados
        item_id = random.randint(100000000, 999999999)
        shop_id = random.randint(1000000, 9999999)
        base_price = random.uniform(1000.0, 5000.0)
        
        mock_nodes.append({
            "item_id": str(item_id),
            "shop_id": str(shop_id),
            "item_name": f"{keyword.capitalize()} Falso Modelo {i+1} - Oficial",
            "item_price": f"{base_price:.2f}",
            "commission_rate": "7.00",
            "image_url": "https://cf.shopee.com.br/file/exemplo_mock.jpg",
            "product_link": f"https://shopee.com.br/product/{shop_id}/{item_id}",
            "offer_link": f"https://shopee.com.br/universal-link/{shop_id}/{item_id}?deep_and_deferred=1"
        })

    # Estrutura exata de resposta GraphQL da Shopee
    return {
        "data": {
            "productOfferV2": {
                "nodes": mock_nodes
            }
        },
        "errors": None
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)