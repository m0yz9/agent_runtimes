import os

from dotenv import load_dotenv
from openai import AsyncOpenAI
from openai.types.responses import Response

load_dotenv()


class LLM:
    def __init__(self, model: str):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model

    # Call the api interface to obtain the Response returned by the OPENAI
    async def chat(self, input: list[dict], tools: list[dict] | None) -> Response:
        response = await self.client.responses.create(
            model=self.model,
            input=input,
            tools=tools,
            reasoning={"effort": "low"},
        )
        return response
