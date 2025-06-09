# app/quotes.py
import logging
import random
from typing import Dict, List

from fastapi import APIRouter, HTTPException, Request

from service.decorators import cached_route, log_route
from service.service import quotes_storage

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/quotes", tags=["Quotes"])
@router.get("/cat?nocache=true", tags=["Service"])
@cached_route("quotes")
@log_route("/quotes")
async def get_quotes(request: Request) -> Dict[str, List[Dict]]:
    force = request.query_params.get("nocache") == "true"
    quotes = quotes_storage.get_all(force_refresh=force)
    if not quotes:
        raise HTTPException(status_code=404, detail={"error": "Цитаты не найдены."})
    return {"quotes": quotes}


@router.get("/quotes/random", tags=["Quotes"])
@router.get("/quotes/random?nocache=true", tags=["Service"])
@cached_route("quotes_random")
@log_route("/quotes/random")
async def get_random_quote(request: Request) -> Dict:
    force = request.query_params.get("nocache") == "true"
    quotes = quotes_storage.get_all(force_refresh=force)
    if quotes:
        return {"quotes": random.choice(quotes)}
    raise HTTPException(status_code=404, detail={"error": "Цитаты не найдены."})


@router.get("/quotes/search", tags=["Quotes"])
@router.get("/quotes/search?nocache=true", tags=["Service"])
@cached_route(
    lambda request, *a, **k: f"quotes_search_{request.query_params.get('author', '').lower()}"
)
@log_route("/quotes/search")
async def search_quote(
    author: str = "", request: Request = None
) -> Dict[str, List[Dict]]:
    force = request.query_params.get("nocache") == "true" if request else False
    quotes = quotes_storage.get_all(force_refresh=force)
    results = [q for q in quotes if author.lower() in q.get("author", "").lower()]
    if results:
        return {"quotes": results}
    raise HTTPException(status_code=404, detail={"error": "Цитаты не найдены."})


@router.get("/quotes/{quote_id}", tags=["Quotes"])
@router.get("/quotes/{quote_id}?nocache=true", tags=["Service"])
@cached_route(lambda request, quote_id, *a, **k: f"quote_{quote_id}")
@log_route("/quotes/{quote_id}")
async def get_quote_by_id(quote_id: int, request: Request) -> Dict[str, Dict]:
    force = request.query_params.get("nocache") == "true"
    quotes = quotes_storage.get_all(force_refresh=force)
    if 0 <= quote_id < len(quotes):
        return {"quotes": quotes[quote_id]}
    raise HTTPException(status_code=404, detail={"error": "Цитаты не найдены."})
