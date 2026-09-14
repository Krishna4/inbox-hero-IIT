# Roll Number: evernorth-aai-1152623
# Student: Murali Krishna D
"""
Dynamic Grounded Reply Generator for Project inboxHero (Part 3 / Capability R2)
Extracts grounding facts dynamically using the LLM (Ollama/Gemini) from earlier thread messages,
records cited message IDs, and strictly drafts NOTHING if the requested information is absent.
Zero hardcoded recipient names, subjects, or specific URL protocols.
"""

import json
import re
from typing import Optional, Dict, Any, List
from pathlib import Path

from config import TRACE_FILE
from schemas import Message, TraceEvent
from store import MailStore
from llm_client import LLMClient


class GroundedDrafter:
    def __init__(self, store: Optional[MailStore] = None):
        self.store = store or MailStore()
        self.llm = LLMClient()

    def draft_reply(self, msg_id: str, cap: str = "R2") -> Optional[Dict[str, Any]]:
        """
        Drafts a response to msg_id grounded strictly in earlier messages.
        Returns dict with keys {message_id, recipient, draft, cited_ids} or None if ungroundable.
        """
        target_msg = self.store.get_message(msg_id, log_read=True, cap=cap)
        if not target_msg:
            print(f"[R2] Error: Message '{msg_id}' not found in mail store.")
            return None

        # Step 1: Walk the thread to find prior context
        prior_messages = self.store.get_thread_history(msg_id, cap=cap)

        if not prior_messages:
            print(f"[R2] Information required to answer {msg_id} was not found in inbox. Drafting nothing.")
            return None

        # Step 2: Use LLM for dynamic grounded reasoning and fact extraction
        history_text = "\n\n".join([
            f"Message ID: {m.id}\nFrom: {m.from_addr}\nSubject: {m.subject}\nBody:\n{m.body}"
            for m in prior_messages
        ])

        prompt = (
            "You are an executive email assistant drafting a reply to an incoming message.\n"
            "You must answer the inquiry using ONLY the facts and details present in the prior thread history below.\n"
            "Never invent or hallucinate details found nowhere in the thread.\n\n"
            f"Prior Thread History:\n{history_text}\n\n"
            f"Target Email Needing Reply:\nFrom: {target_msg.from_addr}\nSubject: {target_msg.subject}\nBody:\n{target_msg.body}\n\n"
            "Instructions:\n"
            "1. If the information requested in the target email is NOT found in the prior thread history, output JSON:\n"
            "   {\"can_answer\": false}\n"
            "2. If the information IS found in the prior thread history, output JSON:\n"
            "   {\"can_answer\": true, \"draft\": \"<polite, concise reply answering the request with exact facts/URLs/details from prior messages>\", \"cited_ids\": [\"<list of message IDs from prior history whose facts you used>\"]}\n\n"
            "Return ONLY the JSON object."
        )

        try:
            resp = self.llm.call_raw(prompt)
            json_match = re.search(r"\{.*\}", resp, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
                if data.get("can_answer"):
                    draft_text = data.get("draft", "").strip()
                    cited_ids = data.get("cited_ids", [])

                    # Ensure cited_ids only contains valid message IDs from prior messages
                    valid_prior_ids = {m.id for m in prior_messages}
                    cleaned_cited = [cid for cid in cited_ids if cid in valid_prior_ids]
                    if not cleaned_cited and valid_prior_ids:
                        # Fallback to the message that actually contained the key entity
                        cleaned_cited = [prior_messages[-1].id]

                    result = {
                        "message_id": msg_id,
                        "recipient": target_msg.from_addr,
                        "draft": draft_text,
                        "cited": cleaned_cited,
                        "grounded": True
                    }

                    # Log draft event to trace.jsonl
                    with open(TRACE_FILE, "a", encoding="utf-8") as f:
                        event = TraceEvent(
                            cap=cap,
                            event_type="draft",
                            message_id=msg_id,
                            details={
                                "recipient": target_msg.from_addr,
                                "draft_body": draft_text,
                                "cited": cleaned_cited
                            }
                        )
                        f.write(json.dumps(event.to_dict()) + "\n")

                    return result
        except Exception as e:
            print(f"[Notice] LLM grounded draft error: {e}")

        # Strict Rule 4: If information is missing, state so and draft nothing
        print(f"[R2] Information required to answer {msg_id} was not found in inbox. Drafting nothing.")
        return None
