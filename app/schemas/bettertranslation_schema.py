from pydantic import BaseModel

class BetterTranslationRequest(BaseModel):
    instruction: str  # 指令
    input: str        # 待處理的輸入

class TranslationWithTagResponse(BaseModel):
    帶有標籤的英文原文: str
    沒有標籤的中文譯文: str
    帶有標籤的中文譯文: str