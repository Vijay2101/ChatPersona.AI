import asyncio

from groq import AsyncGroq
from httpx import Client
http_client = Client()


from httpx import AsyncClient
from groq import AsyncGroq
import asyncio


async def groq0(prompt):
    # Create an asynchronous HTTP client
    async with AsyncClient() as http_client:
        # Pass the async HTTP client to AsyncGroq
        client = AsyncGroq(
            api_key="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",
            http_client=http_client
        )

        # Await the completion creation
        chat_completion = await client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.1-70b-versatile",
            temperature=0,
            # response_format={"type": "json_object"},
            max_tokens=7500, 
            seed=1,
            stream=True,  # Enable streaming
        )
        # Print the incremental deltas returned by the LLM
        async for chunk in chat_completion:
            print(chunk.choices[0].delta.content, end="")  # Stream content
        # res = chat_completion.choices[0].message.content.strip()
        # return res

# Wrapper function to call `groq0` and print the result
async def main():
    result = await groq0("in detail write essay on LLMs")
    print(result)

# Run the main function
asyncio.run(main())