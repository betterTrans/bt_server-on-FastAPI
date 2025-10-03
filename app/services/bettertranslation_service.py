import json, re
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.example_selectors.semantic_similarity import SemanticSimilarityExampleSelector as Selector
from langchain_core.prompts import PromptTemplate
from langchain_core.prompts.few_shot import FewShotPromptTemplate
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser

# 取得【更好的翻譯】
def get_bettertranslation(instruction: str, input: str) -> str:
    try:
        # 設定內嵌模型
        embeddings = OpenAIEmbeddings( # 參考：https://platform.openai.com/docs/guides/embeddings/embedding-models
            #model="text-embedding-ada-002" # （預設模型）每 $1 可處理 12,500 頁（處理 IIO 54 秒，41MB），MTEB 分數 61.0%
            #model="text-embedding-3-small" # 每 $1 可處理 62,500 頁（處理 IIO 52 秒，41MB），MTEB 分數 62.3%
            model="text-embedding-3-large" # 每 $1 可處理 9,615 頁（處理 IIO 84 秒，82MB），MTEB 分數 64.6%
        )

        # 載入 vectorstore
        vectorStore = FAISS.load_local(
            f'{embeddings.model}-20240530.vectorstore.pkl',
            embeddings,
            allow_dangerous_deserialization=True)

        # 載入樣本選擇器
        example_selector = Selector(
            vectorstore=vectorStore, # 每筆資料都有 'instruction', 'input', 'output' 三個欄位
            k=10,
            input_keys=['instruction', 'input'], # 選擇資料時，會用 'instruction', 'input' 這兩個欄位來進行檢索
        )

        # 建立 Example Template
        example_prompt = PromptTemplate(
            template="""英文原文: {instruction}
機器翻譯: {input}
更好的譯文: {output}""",
            input_variables=["instruction", "input", "output"],
        )

        # 建立 Few-Shot Template
        prompt = FewShotPromptTemplate(
            prefix="""根據以下的翻譯規則，把「英文原文」相應的「機器翻譯」，修改成「更好的譯文」：

翻譯規則：
1. 翻譯時，要把英文原文中每個 word 的意思表達出來，不要省略，也不要漏譯。
2. 如果是英文原文中沒出現的 word，不要在翻譯時增添額外的語詞，也不要隨意衍生出額外的譯文。
3. 翻譯成中文時，請盡量使用台灣會使用的詞彙。

<< 回應格式 >>
```json
{{
    "英文原文": string \ 所提供的英文原文
    "機器翻譯": string \ 所提供的機器翻譯
    "更好的譯文": string \ 根據參考範例，對機器翻譯進行修改後的譯文
}}
```

以下是一些範例，請參考這些範例，輸出更好的譯文：""",
            example_selector=example_selector, # 用 'instruction', 'input' 這兩個欄位來檢索範本資料
            example_prompt=example_prompt, # 根據檢索出來的範本資料來建立範本 prompt，其中包含有 'instruction', 'input', 'output' 這三個欄位的資訊
            suffix="""

下面就是本次所要翻譯的英文原文，請修改相應的機器翻譯，輸出更好的譯文。

英文原文: {instruction}
機器翻譯: {input}
更好的譯文:

<< OUTPUT (must include ```json at the start of the response) >>
<< OUTPUT (must end with ```) >>""",
            input_variables=["instruction", "input"],
        )

        # 定義大語言模型
        llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.7) # 參考 https://console.groq.com/docs/models

        # 定義輸出解析器
        output_parser = StrOutputParser()

        # 定義 Chain
        chain = prompt | llm | output_parser

        r = chain.invoke({"instruction": instruction, "input": input})
    except Exception as e:
        print(e, flush=True)
        r = {}

    try:
        json_str = get_json_str(r)
        better_translation = json.loads(json_str).get("更好的譯文", "回應裡找不到更好的譯文")
    except Exception as e:
        print(e, flush=True)
        print(json_str, flush=True)
        better_translation = "回應的結果在進行 JSON 轉換時出錯了！！"

    return better_translation

# 把標籤插入譯文
def insert_tagintotranslation(instruction: str, input: str) -> str:
    prompt_template="""你是一位精通 en 和 zh_tw 這兩種語言的專家。你很瞭解中英文的對應關係。
接下來你會看到一段英文，以及相應的中文翻譯。
在英文的文字裡，會看到一些數字標籤，把某些英文片段包了起來。
在中文的文字裡，並沒有這些數字標籤。
你的工作就是要把英文文字裡的數字標簽，插入到中文的文字裡。

規則如下：

- 英文和中文都要維持原來的文字，不能改變文字。
- 英文與中文的數字標籤必須完全對應，中文的標籤數量必須與英文的標籤數量完全相同，標籤裡的數字也要完美對應。
- 標籤的位置必須互相對應。相同的標籤在中文和英文的文字裡所包圍的片段，意義上必須完全相同。

以下是幾個範例：

輸入的英文: This is a {{0}}book{{/0}}.
輸入的中文: 這是一本書。
輸出的中文: 這是一本{{0}}書{{/0}}。

輸入的英文: I love {{0}}the woman who loves me{{/0}}.
輸入的中文: 我愛這個愛我的女人。
輸出的中文: 我愛{{0}}這個愛我的女人{{/0}}。

輸入的英文: I'll {{0}}go back to Taipei{{/0}} and take my glasses back to school {{1}}tomorrow{{/1}}.
輸入的中文: 明天我會回台北，把我的眼鏡拿回學校。
輸出的中文: {{1}}明天{{/1}}我會{{0}}回台北{{/0}}，把我的眼鏡帶回學校。


<< FORMATTING >>
Return a markdown code snippet with a JSON object formatted to look like:
```json
{{
    "輸入的英文": string \ 就是輸入的英文
    "輸入的中文": string \ 就是輸入的中文
    "輸出的中文": string \ 插入數字標籤後的中文譯文
}}
```

接下來我會提供一段帶有數字標籤的英文，以及一段沒有數字標籤的中文譯文，請按照上面的規則與格式，給出插入數字標籤後的中文譯文。

<< INPUT >>
輸入的英文: ```{instruction}```
輸入的中文: ```{input}```
輸出的中文:

<< OUTPUT (must include ```json at the start of the response) >>
<< OUTPUT (must end with ```) >>"""

    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["instruction", "input"],
    )
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.7) # 參考 https://console.groq.com/docs/models
    chain = prompt | llm
    r = chain.invoke({'instruction': instruction, 'input': input})
    try:
        json_str = get_json_str(r)
        taged_translation = json.loads(json_str).get("輸出的中文", "回應裡找不到輸出的中文")
    except Exception as e:
        print(e, flush=True)
        print(json_str, flush=True)
        taged_translation = "回應的結果在進行 JSON 轉換時出錯了！！"

    return taged_translation

# 公用函式：從回應中取出 json 字串
def get_json_str(response):
    # 取出回應的字串
    if isinstance(response, str): # 回應是字串
        response_str = response
    else: # 回應非字串
        if hasattr(response, 'content'):
            response_str = response.content
        elif 'text' in response:
            response_str = response['text']
        else: # 直接化為 json 字串，前後再加上 ```json 和 ```
            response_str = f"```json\n{json.dumps(response)}\n```"

    # 移除掉 json 字串前後多餘的文字，得出 json 字串
    try:
        json_str = re.search(r'```\s*(?:(?:json)?)\n({[^`]+})\n```', response_str)[1].strip()
    except Exception as e:
        print(e, flush=True)
        print(f"JSON 解析出錯了！回應內容為：{response}", flush=True)
        json_str = json.dumps(response)
    return escape_invalid_backslashes(json_str)

# 公用函式：將不合法的反斜線序列轉換為合法的反斜線序列
def escape_invalid_backslashes(s):
    # 保留這些合法 escape
    valid_escapes = ['\\"', '\\\\', '\\/', '\\b', '\\f', '\\n', '\\r', '\\t']
    # 替換不在合法 escape 列表中的反斜線序列
    def replacer(match):
        seq = match.group(0)
        if seq in valid_escapes:
            return seq  # 合法的就保留
        return '\\\\' + seq[1]  # 非法的加一個斜線變合法

    return re.sub(r'\\.', replacer, s)