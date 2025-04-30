from fastapi import APIRouter
from app.schemas.bettertranslation_schema import BetterTranslationRequest, BetterTranslationResponse, TranslationWithTagResponse
from app.services.bettertranslation_service import get_bettertranslation, insert_tag_into_translation

router = APIRouter()

@router.post("/getbettertranslation", response_model=BetterTranslationResponse)
async def get_better_translation(data: BetterTranslationRequest):
    output = get_bettertranslation(data.instruction, data.input)
    return {
        "英文原文": data.instruction,
        "機器翻譯": data.input,
        "更好的譯文": output
    }

@router.post("/inserttagintotranslation", response_model=TranslationWithTagResponse)
async def inserttagintotranslation(data: BetterTranslationRequest):
    output = insert_tag_into_translation(data.instruction, data.input)
    return {
        "帶有標籤的英文原文": data.instruction,
        "沒有標籤的中文譯文": data.input,
        "輸出的中文": output
    }