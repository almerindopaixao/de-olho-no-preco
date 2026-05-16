import time
import hmac
import hashlib
import httpx
from gql import gql, Client
from gql.transport.httpx import HTTPXAsyncTransport
from typing import Dict, Any

class ShopeeAuth(httpx.Auth):
    def __init__(self, app_id: str, app_secret: str):
        self.app_id = app_id
        self.app_secret = app_secret

    def auth_flow(self, request: httpx.Request):
        timestamp = int(time.time())
        payload_str = request.content.decode('utf-8')
        base_string = f"{self.app_id}{timestamp}{payload_str}"
        
        signature = hmac.new(
            self.app_secret.encode('utf-8'),
            base_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        request.headers['Authorization'] = f"SHA256 Credential={self.app_id}, Signature={signature}, Timestamp={timestamp}"
        request.headers['Content-Type'] = 'application/json'
        
        yield request


class ShopeeAffiliateAPI:
    def __init__(self, app_id: str, app_secret: str, use_mock: bool = False):
        self.base_url = "http://localhost:8001" if use_mock else "https://partner.shopeemobile.com"
        
        transport = HTTPXAsyncTransport(
            url=f"{self.base_url}/open_api/v2/affiliate/product_offer/list",
            auth=ShopeeAuth(app_id, app_secret)
        )
        
        self.client = Client(transport=transport, fetch_schema_from_transport=False)

    async def get_product_offers(self, keyword: str, limit: int = 10, page: int = 1) -> Dict[str, Any]:
        query = gql("""
            query GetOffers($keyword: String!, $limit: Int!, $page: Int!) {
                productOfferV2(keyword: $keyword, page_limit: $limit, page_no: $page) {
                    nodes {
                        item_id
                        shop_id
                        item_name
                        item_price
                        commission_rate
                        image_url
                        product_link
                        offer_link
                    }
                }
            }
        """)
        
        variables = {
            "keyword": keyword,
            "limit": limit,
            "page": page
        }

        print(f"📡 Executando GQL Request para a Shopee...")
        result = await self.client.execute_async(query, variable_values=variables)
        return result
