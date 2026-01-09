from fastapi import APIRouter, HTTPException, UploadFile

from app.schemas.bill import OCRBill, Outing, OutingSplit
from app.services.bill import (
    calculate_balance,
    calculate_outing_split_with_minimal_transactions,
    get_bill_details_from_image,
)

router = APIRouter()


@router.post("/ocr")
async def extract_bill_details_from_image(file: UploadFile) -> OCRBill:
    """
    Extract bill details from an uploaded image file.
    """
    content_type = file.content_type
    if not content_type or not content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image file.")

    with file.file as f:
        content = f.read()
        return get_bill_details_from_image(content, content_type)


@router.post("/split")
async def split(outing: Outing) -> OutingSplit:
    """
    Calculate the optimal split of expenses for an outing.
    """
    balance = calculate_balance(outing)
    outing_split = calculate_outing_split_with_minimal_transactions(balance)
    return outing_split
