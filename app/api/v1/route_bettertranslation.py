from fastapi import APIRouter
from app.schemas.bettertranslation_schema import BetterTranslationRequest, TranslationWithTagResponse
from app.services.bettertranslation_service import insert_tag_into_translation

router = APIRouter()

@router.post("/inserttagintotranslation", response_model=TranslationWithTagResponse)
async def inserttagintotranslation(data: BetterTranslationRequest):
    output = insert_tag_into_translation(data.instruction, data.input)
    return {
        "帶有標籤的英文原文": data.instruction,
        "沒有標籤的中文譯文": data.input,
        "帶有標籤的中文譯文": output
    }