from ollama import Client
import json

# Connect to Ollama (adjust port if needed)
client = Client(host="http://localhost:8091")


# ---------- TOOL: penalty_interest ----------
def penalty_interest(principal: float, annual_rate: float, days_late: int) -> dict:
    """
    Calculate penalty interest for overdue payment.

    - principal: amount in CZK
    - annual_rate: annual interest rate in % (e.g. 12 for 12%)
    - days_late: number of days overdue
    """

    if principal <= 0:
        return {"error": "Principal must be positive."}

    if annual_rate < 0:
        return {"error": "Annual rate cannot be negative."}

    if days_late < 0:
        return {"error": "Days late cannot be negative."}

    # Simple interest calculation, no compounding
    interest = principal * (annual_rate / 100) * (days_late / 365)
    total_due = principal + interest

    return {
        "currency": "CZK",
        "principal": round(principal, 2),
        "annual_rate_percent": round(annual_rate, 2),
        "days_late": days_late,
        "interest": round(interest, 2),
        "total_due": round(total_due, 2),
    }


# ---------- TOOL DEFINITIONS ----------
tools = [
    {
        "type": "function",
        "function": {
            "name": "penalty_interest",
            "description": "Calculate penalty interest for overdue payments in CZK.",
            "parameters": {
                "type": "object",
                "properties": {
                    "principal": {
                        "type": "number",
                        "description": "Amount owed in CZK, e.g. 150000",
                    },
                    "annual_rate": {
                        "type": "number",
                        "description": "Annual penalty interest rate in percent, e.g. 12",
                    },
                    "days_late": {
                        "type": "integer",
                        "description": "Number of days the payment is overdue, e.g. 45",
                    },
                },
                "required": ["principal", "annual_rate", "days_late"],
            },
        },
    },
]


def main():
    # USER INPUT
    user_question = (
        "Calculate penalty interest on a 150000 CZK debt "
        "with 12% annual rate that is 45 days overdue."
    )

    # ---------- 1) FIRST CALL: LLM chooses tool and arguments ----------
    messages = [
        {
            "role": "system",
            "content": (
                "You are a function-calling assistant. "
                "When the user asks about overdue payments, late payments, "
                "penalties, or penalty interest, you MUST call the tool "
                "'penalty_interest'."
            ),
        },
        {"role": "user", "content": user_question},
    ]

    response = client.chat(
        model="llama3.2:latest",
        messages=messages,
        tools=tools,
    )

    print("\nFIRST LLM RESPONSE (raw):")
    print(response)

    message = response.message
    tool_calls = message.tool_calls or []

    if not tool_calls:
        print("\nNo tool calls returned by the LLM.")
        return

    tool_call = tool_calls[0]
    func = tool_call.function
    raw_args = func.arguments

    print("\nTool call from LLM:")
    print("Name :", func.name)
    print("Raw args :", raw_args)

    if func.name != "penalty_interest":
        print("\nLLM requested an unknown tool:", func.name)
        return

    tool_args = {
        "principal": float(raw_args["principal"]),
        "annual_rate": float(raw_args["annual_rate"]),
        "days_late": int(raw_args["days_late"]),
    }

    print("Parsed args :", tool_args)

    # ---------- 2) RUN THE PYTHON TOOL ----------
    result = penalty_interest(**tool_args)

    print("\nTOOL RESULT:")
    print(result)

    if "error" in result:
        print("\nTool returned an error:")
        print(result["error"])
        return

    # ---------- 3) SECOND CALL: Send exact result back to LLM ----------
    final_system_prompt = """
You are a financial assistant.

You will receive exact calculation values from a Python tool.

Rules:
- Do NOT recalculate anything.
- Do NOT change any numbers.
- Use the value called "interest" as the penalty interest.
- Use the value called "total_due" as the total amount due.
- Mention all amounts in CZK.
- Answer in one clear sentence.
- Do NOT output JSON.
"""

    final_user_message = f"""
Original user question:
{user_question}

Use these exact values from the Python tool:
Principal: {result["principal"]} CZK
Annual penalty rate: {result["annual_rate_percent"]}%
Days overdue: {result["days_late"]}
Penalty interest: {result["interest"]} CZK
Total amount due: {result["total_due"]} CZK

Write the final answer using exactly these values.
"""

    final_response = client.chat(
        model="llama3.2:latest",
        messages=[
            {"role": "system", "content": final_system_prompt},
            {"role": "user", "content": final_user_message},
        ],
    )

    print("\nFINAL ANSWER FROM LLM:")
    print(final_response["message"]["content"])


if __name__ == "__main__":
    main()