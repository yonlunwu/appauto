#!/usr/bin/env python
# coding=utf-8

import click
from openai import OpenAI


@click.command()
@click.option("--ip", default="127.0.0.1", show_default=True, help="API服务器IP地址，默认值: 127.0.0.1")
@click.option("--port", required=True, type=int)
@click.option("--api-key", type=str, default=None, show_default=True, help="API-Key")
@click.option("--model", required=True, help="要使用的模型名称")
@click.option(
    "--max-tokens", required=True, show_default=True, type=int, default=1024, help="允许最大 token 数：输入 + 输出"
)
@click.option("--question", required=True, help="要询问的问题")
def main(ip, port, api_key, model, max_tokens, question):
    """
    基于 OpenAI 兼容 API 的命令行客户端工具, 用于向指定模型发送请求并获取响应
    ** 请人为检查是否有乱码 **
    """
    base_url = f"http://{ip}:{port}/v1/"

    client = OpenAI(base_url=base_url, api_key=api_key or "EMPTY")

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": question}],
        stream=True,
        temperature=0.6,
        max_tokens=max_tokens,
    )

    result = ""
    for event in response:
        if len(event.choices) > 0 and event.choices[0].delta.content is not None:
            content = event.choices[0].delta.content
            result += content
            print(content, end="", flush=True)  # 实时输出

    with open("output.log", "w", encoding="utf-8") as logfile:
        logfile.write(result)


if __name__ == "__main__":
    main()
