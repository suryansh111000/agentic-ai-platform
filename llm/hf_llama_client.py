# hf_llama_client.py
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import os
# -------------------------------
# Model setup (local)
# -------------------------------
# print("HF_HOME =", os.environ.get("HF_HOME"))
MODEL_ID = "LiquidAI/LFM2.5-1.2B-Instruct"

# print(f"➡️  Loading model '{MODEL_ID}' locally. This may take a minute...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForCausalLM.from_pretrained(MODEL_ID)

# Automatically use GPU if available, otherwise CPU
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)
print(f"✅ Model loaded on {device}")

# -------------------------------
# call_llm function (kept same API)
# -------------------------------
def call_llm(prompt: str, model_id: str = MODEL_ID) -> str:
    """
    Sends a prompt to the local LiquidAI model and returns the assistant's generated message as a string.
    """

    messages = [
        {"role": "user", "content": prompt}
    ]

    inputs = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
    ).to(device)


    outputs = model.generate(
        **inputs,
        max_new_tokens=200,
        do_sample=False,   # REQUIRED for JSON reliability
    )

    generated_text = tokenizer.decode(
        outputs[0][inputs["input_ids"].shape[-1]:],
        skip_special_tokens=True
    ).strip()

    print("⬅️  Response generated")
    return generated_text

# -------------------------------
# Example usage
# -------------------------------
if __name__ == "__main__":
    test_prompt = "Return a JSON with one task."
    response = call_llm(test_prompt)
    print("Generated output:\n", response)