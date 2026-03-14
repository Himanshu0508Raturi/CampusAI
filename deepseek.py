from openai import OpenAI
import os
nvapi_key = os.getenv("DEEPSEEK_API_KEY")
client = OpenAI(
  base_url = "https://integrate.api.nvidia.com/v1",
  api_key = nvapi_key
)

completion = client.chat.completions.create(
  model="deepseek-ai/deepseek-v3.1-terminus",
  messages=[{"role":"user","content":"What if use you as a llm in a RAG system, how would you perform?"}],
  temperature=0.2,
  top_p=0.7,
  max_tokens=8192,
  extra_body={"chat_template_kwargs": {"thinking":False}},
  stream=True
)

for chunk in completion:
  if not getattr(chunk, "choices", None):
    continue
  if chunk.choices and chunk.choices[0].delta.content is not None:
    print(chunk.choices[0].delta.content, end="")
  

