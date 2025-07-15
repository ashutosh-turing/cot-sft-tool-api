from openai import OpenAI
import os

def get_llm_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")
    return OpenAI(api_key=api_key)

def run_llm_response(system_message, prompt, context, samples):
    llm_client = get_llm_client()
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": prompt}
    ]
    if context:
        messages.append({"role": "user", "content": f"Additional Context:\n{context}"})
    if samples:
        messages.append({"role": "user", "content": f"Sample Inputs/Outputs:\n{samples}"})

    try:
        response = llm_client.chat.completions.create(
            model="gpt-4.1",
            messages=messages,
        )
        # Return the full content as a string
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error in run_llm_response: {e}")
        return f"Error in LLM: {e}"
