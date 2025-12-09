from fastapi import APIRouter

from app.schemas.outing import Outing, OutingSplit
from app.services.outing import (
    calculate_balance,
    calculate_outing_split_with_minimal_transactions,
)

router = APIRouter()


@router.post("/split")
async def split(outing: Outing) -> OutingSplit:
    balance = calculate_balance(outing)
    outing_split = calculate_outing_split_with_minimal_transactions(balance)
    return outing_split
