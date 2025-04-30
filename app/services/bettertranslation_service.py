import json, re
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq

def insert_tag_into_translation(instruction: str, input: str) -> str:
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
    llm = ChatGroq(model="Llama3-70b-8192", temperature=0.7)
    chain = prompt | llm
    r = chain.invoke({'instruction': instruction, 'input': input})
    json_str = get_json_str(r)
    taged_translation = json.loads(json_str).get("輸出的中文", "回應裡找不到輸出的中文")

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
    except:
        print(f"JSON 解析出錯了！回應內容為：{response}")
        json_str = json.dumps(response)
    return json_str