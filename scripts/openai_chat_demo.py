#!/usr/bin/env python
# coding=utf-8

from openai import OpenAI

client = OpenAI(base_url="http://127.0.0.1:30000/v1/", api_key="AMES_fa984233eeb753ad_7d91d6c857ee957edc7cd925552f3cfa")

model = "Kimi-K2-Instruct-FP8-Attn-GPTQ-4b-128g-experts"


content = "介绍一下秦始皇和武则天"
print(len(content))


response = client.chat.completions.create(
    model=model,
    messages=[{"role": "user", "content": content}],
    stream=True,
    temperature=0.6,
    max_tokens=512,
)
re = ""
for event in response:
    print(event)
    if len(event.choices) > 0 and event.choices[0].delta.content is not None:
        re = re + event.choices[0].delta.content
print(re)
with open("output.log", "w") as logfile:
    logfile.write(re)
