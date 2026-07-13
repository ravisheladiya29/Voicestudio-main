"""Local Agent Builder fallback when managed MPS is unavailable.

Whitelabeled / BYOK deployments leave MPS_API_URL empty, so create-from-template
cannot call Dograh cloud. Build a Dograh-shaped starter workflow
(Global + Start + Main Agenda + End) from the user's description instead.
"""

from __future__ import annotations


def _global_prompt(*, call_type: str, use_case: str, activity_description: str) -> str:
    direction = "inbound" if call_type.upper() == "INBOUND" else "outbound"
    if direction == "outbound":
        style_block = """\
## COLD OUTBOUND CALL STYLE

This is a cold outbound information call. In the opening part of the call, your job is to earn the next 20 to 30 seconds of attention, not to dump the full pitch immediately.

- Be warm, crisp, and confident.
- Lead with relevance: who you are, why you are calling, and why this may matter to them.
- If the recipient sounds hesitant, skeptical, or busy, make at most one concise rescue attempt:
  - restate the purpose in one line
  - give one concrete reason it may be useful or relevant
  - ask a low friction permission question like whether they want the 20 second version
- If they still do not want to continue, end politely without pushing.
- Do not sound generic, overexcited, or salesy.
- Do not invent personal facts, prior interactions, or sensitive context that was not provided.
"""
        goal = (
            f"You are Sam. We are doing outbound calls for **{use_case}**. "
            f"Your goal is to explain or discuss **{activity_description}**, "
            "answer related questions where needed, and guide the conversation toward "
            "determining if the recipient is a fit. If the recipient seems busy or hesitant, "
            "briefly restate why the call may be relevant, make one concise attempt to keep "
            "them engaged, and if they still do not want to continue, politely wrap up "
            "without making follow up promises. Keep responses short, 2–3 sentences. "
            "10 - 25 words total."
        )
    else:
        style_block = """\
## INBOUND CALL STYLE

This is an inbound call — the user reached out to you.

- Be warm, crisp, and helpful from the first turn.
- Confirm why they called and guide them through the qualification / support flow.
- If they sound confused, restate how you can help in one line and ask a short clarifying question.
- Do not invent personal facts, prior interactions, or sensitive context that was not provided.
"""
        goal = (
            f"You are Sam. You handle inbound calls for **{use_case}**. "
            f"Your goal is to help with **{activity_description}**, answer related questions, "
            "and guide the conversation toward a clear next step or disposition. "
            "Keep responses short, 2–3 sentences. 10 - 25 words total."
        )

    return f"""## Inputs:

use_case: "{use_case}"
activity_description: "{activity_description}"

## Output:

# Goal (ALWAYS REMEMBER THIS OVERALL GOAL):
{goal}

## Response Language
You are a Voice AI Agent who can speak in multiple languages. Your output is played over TTS, so dont generate special characters. Use very simple and conversational language.

---

{style_block}
---

## HANDLING ASR / TRANSCRIPTION ISSUES

You are speaking on a phone call with a human user. The audio can be noisy and ASR (speech-to-text) can be imperfect. Follow all instructions below carefully.

1. **When the text looks strange or unclear**

   - If the user’s message looks weird, unexpected, or unclear:
     - If you can **guess** what they meant and it does **not** affect your next action, just respond normally.
     - Only ask for clarification if the information:
       - Is important for your next step, or
       - Needs to be saved or is critical to the task.

2. **How to ask for clarification**

   - Be casual and polite.
   - Use phrases like:
     - “sorry, did not catch that.”
     - “hey sorry, some noise there - could you repeat?”
     - “hold on, you are coming choppy.”
   - Do **not** mention transcription / ASR errors.
   - Do **not** repeat the same clarification phrase again and again.

3. **If it seems off but not important**

   - If what they said seems odd but does not matter for your next steps, just continue without asking.

4. **Never use their name**
   - Do not say the user‘s name at all, because it may be misheard or mispronounced.

---

## SUMMARY OF KEY BEHAVIOR

- Speak in informal, relaxed, confident tone.
- Always listen and wait after questions or suggestions.
- Handle ASR noise gracefully; clarify only when needed.
- Acknowledge objections, answer using given info, and then resume where you left off.
- Avoid repetition by always checking your last turn.
- Keep persuasion brief and respectful. Never badger the user.
- Use tool calls with **only** the function syntax and no extra text.

---
"""


def _start_prompt(*, call_type: str) -> str:
    if call_type.upper() == "INBOUND":
        return """# MAIN ACTION POINT AT THIS STAGE

## TO DO LIST:
- Greeting
- Confirm reason for calling
- Earn permission to continue into the main agenda

## CALL FLOW:
This is an inbound call. Greet the caller, introduce yourself briefly, confirm why they reached out, and ask one short clarifying question if needed.

Stay in this node for the opening part of the conversation.
Do not move to Main Agenda immediately after the first user reply.
Use the first 1 to 2 user turns to confirm intent and earn permission to continue.

Move to Main Agenda when the caller is ready to discuss the main topic.
If they called by mistake or do not want to continue, choose End Call.

## Critical rules
- If the last message is not a user message, do not make a tool call.
- Never mix text and tool calls in the same output.
- Your turn must end with either a question or a tool call, never both together.
"""

    return """# MAIN ACTION POINT AT THIS STAGE

## TO DO LIST:
- Greeting
- Intro
- Reason for the call
- Earn permission to continue

## CALL FLOW:
This is a cold outbound call. Your job in the opening is to earn the next 20 to 30 seconds of attention, not to explain everything at once.

Greet the user by saying "hi there", tell them your name and company name, briefly explain why you are calling in a way that sounds relevant to them, ask for their name, and ask whether you can take 20 seconds to explain why you reached out.

Do all of this in a single statement with no breaks, fillers, or change of turn.
If company name is not given, invent a random but relevant company name.

Stay in this node for the opening part of the conversation.
Do not move to Main Agenda immediately after the first user reply.
Use the first 1 to 2 user turns to confirm that you are speaking with the right person and to earn permission to continue the conversation.
If needed, ask one short clarifying question here before moving on.

If they sound hesitant, skeptical, or busy, do not give up immediately.
Make at most one concise persuasive attempt:
- restate the reason for the call in one line
- mention one concrete benefit or relevance point
- ask a low friction question such as whether they want the 20 second version

After one concise attempt, either move forward if they engage or end politely if they are clearly not interested.

Move to Main Agenda only when the recipient is willing to hear more or has engaged on the topic.

If it is a wrong number, wrong person, or the user does not want to continue after the brief attempt, choose End Call.

## Critical rules
- If the last message is not a user message, do not make a tool call.
- Never mix text and tool calls in the same output.
- Your turn must end with either a question or a tool call, never both together.
"""


def _agenda_prompt(*, use_case: str, activity_description: str) -> str:
    return f"""# MAIN ACTION POINT AT THIS STEP:
## Usable details and Main Agenda

Details:
[[ {activity_description} ]]

Relevant Questions:
[[ What is your current process related to {use_case}? ]]
[[ What challenges are you facing that you would like to solve? ]]
[[ What would a good next step look like for you? ]]

Wrap up details:
[[ To conclude, briefly recap how this relates to {use_case}. Ask if they have any more questions or want to discuss next steps. Thank them for their time. ]]

## Flow of call
This node owns the full working part of the conversation.
Start by acknowledging the opening and then explain the main topic clearly.
Share the relevant information in a concise way, ask focused follow up questions where needed, and answer the user's questions before moving on.
If they raise objections or ask for clarification, handle that first and then continue the main topic.

Stay in this node until the main discussion is complete.
There is no separate summary node.
This node also owns the light wrap up:
- give a short recap of the main points
- ask if there is anything else they want to know

If they have another related question, continue in this same node.
Move to End Call only when the user is done and there is nothing else to discuss.

## Constraints
- Do not ask the same question again if the user already answered it.
- Do not promise an email, callback, ticket number, or any follow up unless that capability is explicitly available.
- Never mix text and tool calls in the same output.
"""


_END_PROMPT = """# Main Action Point for This Stage

At this stage, the conversation with the user is complete. They have no further questions. Your job is to end the call politely and immediately. Do **not** start any new topics. Even if there are unresolved threads, you must ignore them and proceed to close the conversation. Do **not** wait for the user, do **not** ask questions, and do **not** hand the turn back to them.


**Generate a brief response (6–8 words)** that naturally follows from the user’s last message. Example: "Thank you for the call. And have - a wonderful day"

After this, say nothing else. The call is over.
"""


def build_local_workflow_from_description(
    *,
    call_type: str,
    use_case: str,
    activity_description: str,
) -> dict:
    """Return {name, workflow_definition} matching Dograh's Agent Builder shape."""
    use_case = use_case.strip()
    activity_description = activity_description.strip()
    direction = "inbound" if call_type.upper() == "INBOUND" else "outbound"
    name = f"{use_case} - {direction}"

    workflow_definition = {
        "nodes": [
            {
                "id": "0",
                "type": "globalNode",
                "position": {"x": -325, "y": 480},
                "data": {
                    "prompt": _global_prompt(
                        call_type=call_type,
                        use_case=use_case,
                        activity_description=activity_description,
                    ),
                    "name": "Global Node",
                    "allow_interrupt": False,
                    "invalid": False,
                    "validationMessage": None,
                    "is_static": False,
                },
            },
            {
                "id": "1",
                "type": "startCall",
                "position": {"x": 175, "y": 60},
                "data": {
                    "prompt": _start_prompt(call_type=call_type),
                    "name": "Start Call",
                    "allow_interrupt": False,
                    "invalid": False,
                    "validationMessage": None,
                    "is_static": False,
                    "add_global_prompt": True,
                    "wait_for_user_response": False,
                    "detect_voicemail": False,
                    "delayed_start": False,
                    "is_start": True,
                },
            },
            {
                "id": "2",
                "type": "agentNode",
                "position": {"x": 615.5, "y": 476},
                "data": {
                    "prompt": _agenda_prompt(
                        use_case=use_case,
                        activity_description=activity_description,
                    ),
                    "name": "Main Agenda and Questions",
                    "allow_interrupt": False,
                    "invalid": False,
                    "validationMessage": None,
                    "extraction_enabled": False,
                    "extraction_prompt": "",
                    "extraction_variables": [],
                    "add_global_prompt": True,
                },
            },
            {
                "id": "4",
                "type": "endCall",
                "position": {"x": 175, "y": 900},
                "data": {
                    "prompt": _END_PROMPT,
                    "name": "End Call",
                    "allow_interrupt": False,
                    "invalid": False,
                    "validationMessage": None,
                    "is_static": False,
                    "extraction_enabled": False,
                    "extraction_prompt": "",
                    "extraction_variables": [],
                    "add_global_prompt": False,
                    "is_end": True,
                },
            },
        ],
        "edges": [
            {
                "id": "1-2",
                "animated": True,
                "type": "custom",
                "source": "1",
                "target": "2",
                "data": {
                    "condition": (
                        "Choose this pathway when you have introduced yourself, "
                        "learned who you are speaking with, and confirmed enough "
                        "context to move into the main topic of the call."
                    ),
                    "label": "Move to Main Agenda",
                    "invalid": False,
                    "validationMessage": None,
                },
            },
            {
                "id": "1-4",
                "animated": True,
                "type": "custom",
                "source": "1",
                "target": "4",
                "data": {
                    "condition": (
                        "Choose this pathway whenever you are supposed to end the "
                        "call from the opening stage, such as a wrong number, wrong "
                        "person, or the user does not want to continue."
                    ),
                    "label": "End call",
                    "invalid": False,
                    "validationMessage": None,
                },
            },
            {
                "id": "2-4",
                "animated": True,
                "type": "custom",
                "source": "2",
                "target": "4",
                "data": {
                    "condition": (
                        "Choose this pathway whenever the main topic has been "
                        "covered and the user has nothing else to discuss."
                    ),
                    "label": "End call",
                    "invalid": False,
                    "validationMessage": None,
                },
            },
        ],
        "viewport": {"x": 22, "y": -54, "zoom": 0.7},
    }

    return {
        "name": name[:120],
        "workflow_definition": workflow_definition,
    }
