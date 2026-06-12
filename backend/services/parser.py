import re
import json
import anthropic
from config import ANTHROPIC_API_KEY

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """You are a transaction parser for small African shops and pharmacies.
Your job is to extract structured transaction data from informal messages sent by shop owners.

Messages may be in English, Nigerian Pidgin, or a mix. They describe sales, credit given to customers, or restocks.

You must return ONLY valid JSON — no explanation, no markdown, no extra text.

Return this exact structure:
{
  "parse_status": "parsed",
  "transactions": [
    {
      "product_name": "string",
      "quantity": 1,
      "unit_price": null,
      "transaction_type": "sale",
      "customer_name": null,
      "is_credit": false,
      "notes": null
    }
  ],
  "ambiguity_reason": null
}

Rules:
- One message can contain multiple transactions — split them into separate objects in the array.
- If a customer name is mentioned with an amount, it is a credit transaction. Set is_credit to true and transaction_type to credit.
- If a price is not mentioned, set unit_price to null.
- If the message is completely unreadable, set parse_status to failed and transactions to empty array.
- If something is unclear but you made a reasonable guess, set parse_status to ambiguous and explain in ambiguity_reason.
- Never invent product names. Use exactly what the owner wrote.
- Quantities like x20, 20 packs, twenty should all become the number 20.
- Common Nigerian product shorthand: para = Paracetamol, indom = Indomie, tomi = Tomato paste.
- For credit transactions where no product is specified, set product_name to CREDIT.
"""

def strip_markdown(text: str) -> str:
    text = text.strip()
    text = re.sub(r'^```(?:json)?\s*', '', text)
    text = re.sub(r'\s*```$', '', text)
    return text.strip()

def parse_transaction(raw_message: str) -> dict:
    try:
        print(f"[PARSER] Sending to LLM: {raw_message}")
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": raw_message}]
        )
        text = strip_markdown(response.content[0].text)
        print(f"[PARSER] LLM response: {text}")
        result = json.loads(text)
        return result
    except json.JSONDecodeError as e:
        print(f"[PARSER] JSON error: {e}")
        return {
            "parse_status": "failed",
            "transactions": [],
            "ambiguity_reason": "LLM returned non-JSON response"
        }
    except Exception as e:
        print(f"[PARSER] Exception {type(e).__name__}: {e}")
        return {
            "parse_status": "failed",
            "transactions": [],
            "ambiguity_reason": str(e)
        }
