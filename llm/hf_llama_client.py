import os
import time
from openai import OpenAI

# ✅ Initialize client (HF Router)
client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=os.getenv("HF_TOKEN") or os.getenv("HF_API_TOKEN"),
)

# ✅ Model (with provider)
MODEL = "mistralai/Mistral-7B-Instruct-v0.2:featherless-ai"


def call_llm(prompt: str, retries: int = 3) -> str:
    for attempt in range(retries + 1):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2,
                max_tokens=400
            )

            content = response.choices[0].message.content.strip()

            if content:
                print("⬅️ Response generated")
                return content
            else:
                print(f"⚠ Empty response, retrying...")

        except Exception as e:
            print(f"⚠ Attempt {attempt+1} failed: {e}")
            time.sleep(1)

    raise RuntimeError("LLM API failed after retries")


# -------------------------------
# Example usage
# -------------------------------
if __name__ == "__main__":
    test_prompt = "Return a JSON with one task."
    response = call_llm(test_prompt)
    print("Generated output:\n", response)