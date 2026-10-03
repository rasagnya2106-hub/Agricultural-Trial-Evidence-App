import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

from tools import (
    search_trials,
    compare_trials,
    find_evidence,
    get_trial_sources,
)


load_dotenv()


# =========================================================
# GEMINI SETUP
# =========================================================

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY is not configured in .env"
    )

client = genai.Client(api_key=api_key)

MODEL_NAME = "gemini-3.8-flash"


# =========================================================
# GEMINI TOOL DECLARATIONS
# =========================================================

search_trials_declaration = types.FunctionDeclaration(
    name="search_trials",
    description=(
        "Search agricultural trial records using filters. "
        "Use this for questions asking which trials exist."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "crop": types.Schema(
                type=types.Type.STRING,
                description="Crop name."
            ),
            "product": types.Schema(
                type=types.Type.STRING,
                description="Product name."
            ),
            "country": types.Schema(
                type=types.Type.STRING,
                description="Country name."
            ),
            "year": types.Schema(
                type=types.Type.INTEGER,
                description="Trial year."
            ),
            "trial_type": types.Schema(
                type=types.Type.STRING,
                description="Scientific or Demonstration."
            ),
        },
    ),
)


compare_trials_declaration = types.FunctionDeclaration(
    name="compare_trials",
    description=(
        "Compare treatment and control yields for selected "
        "trial IDs and calculate the yield difference."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "trial_ids": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(
                    type=types.Type.STRING
                ),
                description="Trial IDs to compare."
            ),
        },
        required=["trial_ids"],
    ),
)


find_evidence_declaration = types.FunctionDeclaration(
    name="find_evidence",
    description=(
        "Find evidence for a crop and product combination."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "crop": types.Schema(
                type=types.Type.STRING,
                description="Crop name."
            ),
            "product": types.Schema(
                type=types.Type.STRING,
                description="Product name."
            ),
        },
    ),
)


get_trial_sources_declaration = types.FunctionDeclaration(
    name="get_trial_sources",
    description=(
        "Retrieve the original source records for a trial. "
        "Use this when source details or conflicts need checking."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "trial_id": types.Schema(
                type=types.Type.STRING,
                description="Trial ID such as T01 or T03."
            ),
        },
        required=["trial_id"],
    ),
)


trial_tools = types.Tool(
    function_declarations=[
        search_trials_declaration,
        compare_trials_declaration,
        find_evidence_declaration,
        get_trial_sources_declaration,
    ]
)


# =========================================================
# TOOL EXECUTION
# =========================================================

def execute_tool(name, arguments):

    if name == "search_trials":
        return search_trials(**arguments)

    if name == "compare_trials":
        return compare_trials(**arguments)

    if name == "find_evidence":
        return find_evidence(**arguments)

    if name == "get_trial_sources":
        return get_trial_sources(**arguments)

    return {
        "error": f"Unknown tool: {name}"
    }


# =========================================================
# FALLBACK ANSWER
# =========================================================

def build_fallback_answer(question, tool_activity):

    if not tool_activity:
        return (
            "I could not retrieve agricultural trial evidence "
            "for this question."
        )

    last_activity = tool_activity[-1]

    tool_name = last_activity["tool"]
    result = last_activity["result"]

    # -----------------------------------------------------
    # Search results
    # -----------------------------------------------------

    if tool_name == "search_trials":

        if not result:
            return (
                "No matching agricultural trial records were "
                "found in the supplied dataset."
            )

        lines = [
            f"I found {len(result)} matching trial(s) in the supplied dataset:"
        ]

        for trial in result:
            treatment = trial.get("treatment_yield_kg_ha")
            control = trial.get("control_yield_kg_ha")

            line = (
                f"- {trial['trial_id']}: "
                f"{trial['crop']}, "
                f"{trial['product']}, "
                f"{trial['country']}, "
                f"{trial['year']}, "
                f"{trial['trial_type']}"
            )

            if treatment is not None:
                line += f", treatment {treatment:,.0f} kg/ha"

            if control is not None:
                line += f", control {control:,.0f} kg/ha"

            lines.append(line)

        lines.append(
            "\nThese results come from the normalized trial database."
        )

        return "\n".join(lines)

    # -----------------------------------------------------
    # Comparison results
    # -----------------------------------------------------

    if tool_name == "compare_trials":

        if not result:
            return (
                "No matching trial IDs were found for comparison."
            )

        lines = ["Trial comparison from the supplied evidence:"]

        for trial in result:

            line = (
                f"- {trial['trial_id']} — "
                f"{trial['country']} ({trial['year']}): "
            )

            treatment = trial.get("treatment_yield_kg_ha")
            control = trial.get("control_yield_kg_ha")
            difference = trial.get("absolute_change_kg_ha")
            percentage = trial.get("percentage_change")

            if treatment is None or control is None:
                line += "control or treatment yield is missing."
            else:
                line += (
                    f"treatment {treatment:,.0f} kg/ha, "
                    f"control {control:,.0f} kg/ha, "
                    f"difference {difference:,.0f} kg/ha"
                )

                if percentage is not None:
                    line += f" ({percentage:.2f}%)."

            lines.append(line)

        return "\n".join(lines)

    # -----------------------------------------------------
    # Evidence results
    # -----------------------------------------------------

    if tool_name == "find_evidence":

        if not result:
            return (
                "No supplied trial evidence was found for this "
                "crop and product combination."
            )

        lines = [
            f"I found {len(result)} relevant trial record(s):"
        ]

        for trial in result:

            treatment = trial.get(
                "treatment_yield_kg_ha"
            )

            control = trial.get(
                "control_yield_kg_ha"
            )

            difference = trial.get(
                "yield_difference_kg_ha"
            )

            line = (
                f"- {trial['trial_id']}: "
                f"{trial['crop']} / "
                f"{trial['product']} / "
                f"{trial['country']} / "
                f"{trial['year']} / "
                f"{trial['trial_type']}"
            )

            if treatment is not None:
                line += (
                    f"; treatment {treatment:,.0f} kg/ha"
                )

            if control is not None:
                line += (
                    f"; control {control:,.0f} kg/ha"
                )

            if difference is not None:
                line += (
                    f"; difference {difference:,.0f} kg/ha"
                )

            lines.append(line)

            notes = trial.get("notes")

            if notes:
                lines.append(
                    f"  Note: {notes}"
                )

        return "\n".join(lines)

    # -----------------------------------------------------
    # Original source results
    # -----------------------------------------------------

    if tool_name == "get_trial_sources":

        if not result:
            return (
                "No original source records were found for "
                "that trial ID."
            )

        lines = [
            f"Original source records found: {len(result)}"
        ]

        for source in result:

            lines.append(
                f"- {source['source']} "
                f"({source['source_type']}): "
                f"treatment="
                f"{source['treatment_yield_kg_ha']}, "
                f"control="
                f"{source['control_yield_kg_ha']}"
            )

            if source.get("notes"):
                lines.append(
                    f"  Note: {source['notes']}"
                )

        return "\n".join(lines)

    return (
        "The requested evidence was retrieved, but the AI "
        "response could not be generated."
    )


# =========================================================
# SAFE GEMINI REQUEST
# =========================================================

def send_message_with_retry(chat, message, retries=2):

    for attempt in range(retries + 1):

        try:
            return chat.send_message(message)

        except Exception as error:

            error_text = str(error)

            if "503" not in error_text and "UNAVAILABLE" not in error_text:
                raise

            if attempt == retries:
                raise

            wait_seconds = 2 * (attempt + 1)

            print(
                f"\n[Gemini temporarily unavailable]"
                f" Retrying in {wait_seconds} seconds..."
            )

            time.sleep(wait_seconds)

    return None


# =========================================================
# AGENT
# =========================================================

def ask_agent(question):

    system_instruction = """
You are an agricultural trial evidence assistant.

Use the available tools to answer questions about agricultural
trial records.

Important rules:

- Use tools for factual information.
- Never invent trial records.
- Never invent yield values.
- Missing values are not zero.
- Preserve conflicting source values.
- Mention trial IDs when relevant.
- Use original sources when source verification is required.
- Use the minimum number of tools needed.
- For a simple listing question, search_trials is usually enough.
- For comparison questions, use search_trials and then
  compare_trials when trial IDs are known.
- For source or conflict questions, use get_trial_sources.
- If the database does not contain enough evidence, say so.
"""

    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        tools=[trial_tools],
    )

    chat = client.chats.create(
        model=MODEL_NAME,
        config=config,
    )

    tool_activity = []

    # -----------------------------------------------------
    # First request
    # -----------------------------------------------------

    try:
        response = send_message_with_retry(
            chat,
            question,
        )

    except Exception as error:

        error_text = str(error)

        if (
            "503" in error_text
            or "UNAVAILABLE" in error_text
            or "429" in error_text
            or "RESOURCE_EXHAUSTED" in error_text
        ):
            return {
                "answer": (
                    "The AI model is temporarily unavailable. "
                    "Please try the question again in a moment."
                ),
                "tool_activity": [],
                "error": "Gemini 503 UNAVAILABLE",
            }

        raise

    # -----------------------------------------------------
    # Tool loop
    # -----------------------------------------------------

    for step in range(6):

        function_calls = []

        for part in response.candidates[0].content.parts:

            if part.function_call:
                function_calls.append(
                    part.function_call
                )

        # No function call means Gemini produced
        # the final answer.
        if not function_calls:
            break

        function_responses = []

        for function_call in function_calls:

            name = function_call.name

            arguments = dict(
                function_call.args
            )

            print(
                f"\n[Tool Call] {name}"
            )

            print(
                f"[Arguments] {arguments}"
            )

            result = execute_tool(
                name,
                arguments,
            )

            result_count = (
                len(result)
                if isinstance(result, list)
                else "received"
            )

            print(
                f"[Tool Result] {result_count}"
            )

            tool_activity.append({
                "step": step + 1,
                "tool": name,
                "arguments": arguments,
                "result": result,
            })

            function_responses.append(
                types.Part.from_function_response(
                    name=name,
                    response={
                        "result": result
                    },
                )
            )

        # -------------------------------------------------
        # Send tool results back to Gemini
        # -------------------------------------------------

        try:

            response = send_message_with_retry(
                chat,
                function_responses,
            )

        except Exception as error:

            error_text = str(error)

            if (
                "503" in error_text
                or "UNAVAILABLE" in error_text
                or "429" in error_text
                or "RESOURCE_EXHAUSTED" in error_text
            ):

                print(
                    "\n[Gemini 503]"
                    " Using evidence-based fallback answer."
                )

                return {
                    "answer": build_fallback_answer(
                        question,
                        tool_activity,
                    ),
                    "tool_activity": tool_activity,
                    "fallback": True,
                }

            raise

    # -----------------------------------------------------
    # Final response
    # -----------------------------------------------------

    return {
        "answer": response.text,
        "tool_activity": tool_activity,
    }


# =========================================================
# TERMINAL TEST
# =========================================================

if __name__ == "__main__":

    question = input(
        "\nAsk a question about the agricultural trials:\n> "
    )

    result = ask_agent(question)

    print("\n")
    print("=" * 60)
    print("TOOL ACTIVITY")
    print("=" * 60)

    for activity in result["tool_activity"]:

        print(
            f"\nStep {activity['step']}"
        )

        print(
            f"Tool: {activity['tool']}"
        )

        print(
            f"Arguments: {activity['arguments']}"
        )

    print("\n")
    print("=" * 60)
    print("FINAL ANSWER")
    print("=" * 60)

    print(result["answer"])