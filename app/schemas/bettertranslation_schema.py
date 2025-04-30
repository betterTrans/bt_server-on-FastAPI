from pydantic import BaseModel

# 【更好的譯文】請求格式
class BetterTranslationRequest(BaseModel):
    instruction: str  # 指令
    input: str        # 待處理的輸入

# 【更好的譯文】回應格式
class BetterTranslationResponse(BaseModel):
    英文原文: str
    機器翻譯: str
    更好的譯文: str

# 【帶有標籤的譯文】回應格式
class TranslationWithTagResponse(BaseModel):
    帶有標籤的英文原文: str
    沒有標籤的中文譯文: str
    輸出的中文: str