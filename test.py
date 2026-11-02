import asyncio

from agent_runtimes.agent.llm import LLM


async def main():
    llm = LLM(model="gpt-6-luna")

    input_items = [
        {
            "role": "user",
            "content": "我叫iwang",
        },
    ]
    response = await llm.chat(input_items, None)
    input_items.extend(response.output)

    input_items.append(
        {
            "role": "user",
            "content": "我叫什么",
        }
    )

    resp = await llm.chat(input_items, None)
    print(resp.output_text)
    # input_items.append(
    #     {
    #         "role": "user",
    #         "content": "我叫什么？",
    #     }
    # )
    # resp = await llm.chat(input_items, None)

    # print(resp.output_text)


if __name__ == "__main__":
    asyncio.run(main())
