import json
import re
import math

from app.services.ai.roberta_activity_classifier import RobertaActivityClassifier
from app.specifications.activity_types import ActivityType
from app.models.user_right_type import UserRightType


class ActivityClassifier:

    # ------------------------------------------------
    # JSON extractor robusto
    # ------------------------------------------------

    @staticmethod
    def _extract_json(text):

        if not text:
            return "{}"

        start = text.find("{")

        if start == -1:
            return "{}"

        brace_count = 0

        for i in range(start, len(text)):

            if text[i] == "{":
                brace_count += 1

            elif text[i] == "}":
                brace_count -= 1

                if brace_count == 0:
                    return text[start:i+1]

        return text[start:]
    

    @staticmethod
    def _clean_llm_json(text):

        if not text:
            return "{}"

        # eliminar comentarios //
        text = re.sub(r"//.*", "", text)

        # eliminar comentarios tipo /* */
        text = re.sub(r"/\*[\s\S]*?\*/", "", text)

        # quitar trailing commas
        text = re.sub(r",\s*}", "}", text)
        text = re.sub(r",\s*]", "]", text)

        return text

    # ------------------------------------------------
    # profile simplification (important for Phi-3)
    # ------------------------------------------------

    @staticmethod
    def _collect_dataset_attributes(activity_profiles):

        attrs = set()

        for p in activity_profiles:

            for k in p.get("example_attributes", {}).keys():
                attrs.add(k)

        return sorted(list(attrs))
    
    @staticmethod
    def _simplify_profiles(activity_profiles):
        simplified = []
        for p in activity_profiles:
            name = p.get("name")
            attrs = p.get("example_attributes", {})
            
            # Solo enviamos las llaves (nombres de los atributos)
            # Esto reduce drásticamente los tokens y evita confusiones con los conteos
            filtered_keys = [k for k in attrs.keys()]

            simplified.append({
                "name": name,
                "attributes": filtered_keys
            })
        return simplified
    

    @staticmethod
    def _format_profiles_for_prompt(profiles):

        lines = []

        for p in profiles:

            attrs = ", ".join(p["attributes"])

            line = f"{p['name']} -> [{attrs}]"

            lines.append(line)

        return "\n".join(lines)

    # ------------------------------------------------
    # PARSER ROBUSTO
    # ------------------------------------------------

    @staticmethod
    def _parse_llm_output(data):

        mapping = {}

        # CASE 1
        if isinstance(data, dict) and "activities" in data:

            activities = data["activities"]

            if isinstance(activities, list):

                for a in activities:

                    if not isinstance(a, dict):
                        continue

                    name = a.get("name") or a.get("activity")
                    label = a.get("type")

                    if not name:
                        continue

                    try:
                        mapping[name] = {
                            "activity_type": ActivityType[label],
                            "user_right_type": None
                        }
                    except Exception:
                        mapping[name] = {
                            "activity_type": ActivityType.OTHER,
                            "user_right_type": None
                        }

        # CASE 2
        elif isinstance(data, dict):

            for name, label in data.items():

                try:
                    mapping[name] = {
                        "activity_type": ActivityType[label],
                        "user_right_type": None
                    }
                except Exception:
                    mapping[name] = {
                        "activity_type": ActivityType.OTHER,
                        "user_right_type": None
                    }

        # CASE 3
        elif isinstance(data, list):

            for a in data:

                if not isinstance(a, dict):
                    continue

                name = a.get("name") or a.get("activity")
                label = a.get("type")

                if not name:
                    continue

                try:
                    mapping[name] = {
                        "activity_type": ActivityType[label],
                        "user_right_type": None
                    }
                except Exception:
                    mapping[name] = {
                        "activity_type": ActivityType.OTHER,
                        "user_right_type": None
                    }

        return mapping

    # ------------------------------------------------
    # USER RIGHTS SUBCLASSIFIER
    # ------------------------------------------------

    @staticmethod
    def _infer_user_right_subtype(activity_name):
        return RobertaActivityClassifier._classify_user_right(
            activity_name,
            f"Activity name: {activity_name}."
        )

    @staticmethod
    def _infer_user_right_subtype_with_phi3(activity_name):

        prompt = f"""
You are an expert in GDPR data subject rights.

Your task is to classify an activity into ONE GDPR data subject right.

Activity:
{activity_name}

Possible labels:

ACCESS
RECTIFICATION
ERASURE
RESTRICTION
PORTABILITY
OBJECTION
AUTOMATED_DECISION_REVIEW
INFORMATION
UNKNOWN

Definitions:

ACCESS:
Request to obtain, consult, or receive a copy of personal data.

RECTIFICATION:
Correct, update, or complete inaccurate personal data.

ERASURE:
Delete, erase, remove, or permanently destroy personal data.

RESTRICTION:
Temporarily suspend, block, or limit processing activities.

PORTABILITY:
Export, transfer, or provide personal data in a reusable structured format.

OBJECTION:
Object to processing, oppose marketing, or stop a specific processing activity.

AUTOMATED_DECISION_REVIEW:
Request human intervention or review of an automated decision or profiling activity.

INFORMATION:
Request information or transparency about how personal data is collected, used, stored, or shared.

UNKNOWN:
The activity is not clearly related to a GDPR data subject right.

STRICT RULES:
- Return ONLY one label from the list above.
- Do NOT invent new labels.
- Do NOT explain your answer.
- If uncertain, return UNKNOWN.

Return ONLY valid JSON:

{{
    "type": "ACCESS"
}}
"""

        from app.services.llm_client import LLMClient

        response = LLMClient.ask(prompt)

        print("\n===== USER RIGHT SUBTYPE RAW =====")
        print(activity_name)
        print(response)

        response = ActivityClassifier._extract_json(response)

        response = ActivityClassifier._clean_llm_json(response)

        try:

            data = json.loads(response)

            label = data.get("type", "UNKNOWN")

            return UserRightType[label]

        except Exception:

            print("\n⚠ USER RIGHT SUBTYPE ERROR")
            print(response)

            return UserRightType.UNKNOWN
        

    # ------------------------------------------------
    # MAIN CLASSIFIER
    # ------------------------------------------------

    @staticmethod
    def classify(activity_profiles, dataset_context=None):

        if not activity_profiles:
            return {}

        try:
            return RobertaActivityClassifier.classify(
                activity_profiles,
                dataset_context
            )
        except Exception as exc:
            print("RoBERTa activity classification error")
            print(exc)
            return {
                profile["name"]: {
                    "activity_type": ActivityType.OTHER,
                    "user_right_type": None
                }
                for profile in activity_profiles
                if profile.get("name")
            }

    @staticmethod
    def classify_with_phi3(activity_profiles, dataset_context=None):

        if not activity_profiles:
            return {}

        context_text = (
            dataset_context
            if dataset_context
            else "No additional dataset context provided."
        )

        simplified_profiles = ActivityClassifier._simplify_profiles(activity_profiles)

        activity_names = json.dumps([p["name"] for p in simplified_profiles])
        print("\n===== ACTIVITY NAMES =====")
        print(activity_names)

        dataset_attributes = ActivityClassifier._collect_dataset_attributes(
            activity_profiles
        )

        attributes_json = json.dumps(dataset_attributes)

        print("\n===== ATRIBUTES =====")
        print(dataset_attributes)
        # ------------------------------------------------
        # PROMPT
        # ------------------------------------------------

        prompt = f"""
You are an expert in GDPR process analysis and process mining.

Your task is to classify activities of an event log into GDPR ActivityTypes. 
The dataset can belong to any domain (Healthcare, Fintech, HR, Logistics, etc.).

--------------------------------
DATASET CONTEXT
--------------------------------
{context_text}

--------------------------------
ACTIVITIES & ATTRIBUTES
--------------------------------
Activities to classify: {activity_names}

Global attributes observed in this process:
{attributes_json}

--------------------------------
ActivityType Definitions & Critical Rules
--------------------------------

DATA_COLLECTION: Primary entry point. Registration, enrollment, or first-time intake of subject data.
DATA_ACCESS: Pure consultation or "viewing" activities without modifying or generating new values.
DATA_PROCESSING: (BROADEST) Any activity where data is used to perform a task, evaluate, diagnose, treat, or calculate. Most operational steps fall here.
AUTOMATED_DECISION: Specific steps where a system makes a final decision (e.g., "Score Approval", "Auto-Diagnosis").
DATA_TRANSFER: Movement of data to external parties, third-party APIs, or different legal entities.
STORAGE_MANAGEMENT: Technical storage tasks. Note: Moving a case to a "closed" state in a database is NOT always deletion.
USER_RIGHT_REQUEST: Specific GDPR rights (Right to be forgotten, portability, access request).
DATA_DELETION: Permanent removal, shredding, or anonymization. Administrative "Release", "Discharge", "End of Process" or "Closing a case" is NOT DATA_DELETION unless explicitly stated as "Purge" or "Destroy".

--------------------------------
Classification Strategy
--------------------------------
- Use the "Principle of Persistence": In business processes, data usually persists after the process ends for legal compliance. Therefore, "Closing", "Finishing", or "Releasing" a subject should usually be classified as DATA_PROCESSING or STORAGE_MANAGEMENT, never as DELETION.
- Contextual Inference: If the domain is 'Healthcare', activities like 'Leucocytes' or 'Triage' are DATA_PROCESSING (medical evaluation). 
- If an activity marks the end of a lifecycle but the data remains in records, use DATA_PROCESSING or STORAGE_MANAGEMENT.

--------------------------------
Return ONLY JSON
--------------------------------
{{
  "activities":[
    {{"name":"activity name","type":"ActivityType", "reasoning": "brief 5-word explanation"}}
  ]
}}

--------------------------------
Example
--------------------------------

Input:
["User Registration","Blood Test","Loan Approval"]

Output:

{{
 "activities":[
  {{"name":"User Registration","type":"DATA_COLLECTION"}},
  {{"name":"Blood Test","type":"DATA_PROCESSING"}},
  {{"name":"Loan Approval","type":"AUTOMATED_DECISION"}}
 ]
}}

--------------------------------
FINAL STRICTURES
--------------------------------
- Ensure the JSON is syntactically correct and complete.
- Do NOT include markdown code blocks (```json). Return raw text only.
- Every activity in the input list MUST be present in the output.
"""

        # ------------------------------------------------
        # LLM CALL
        # ------------------------------------------------

        from app.services.llm_client import LLMClient

        response = LLMClient.ask(prompt)

        print("\n===== LLM CLASSIFICATION RAW =====")
        print(response)
        print("==================================\n")

        response = ActivityClassifier._extract_json(response)

        response = ActivityClassifier._clean_llm_json(response)

        try:

            data = json.loads(response)

        except Exception:

            print("\n⚠ Activity classification JSON error")
            print(response)

            return {
                p["name"]: ActivityType.OTHER
                for p in activity_profiles
            }

        mapping = ActivityClassifier._parse_llm_output(data)

        # ------------------------------------------------
        # USER RIGHTS SECOND PASS
        # ------------------------------------------------

        for activity_name, info in mapping.items():

            activity_type = info["activity_type"]

            if activity_type != ActivityType.USER_RIGHT_REQUEST:
                continue

            subtype = ActivityClassifier._infer_user_right_subtype(
                activity_name
            )

            info["user_right_type"] = subtype

        # ------------------------------------------------
        # COMPLETE MISSING ACTIVITIES
        # ------------------------------------------------

        for profile in activity_profiles:

            name = profile["name"]

            if name not in mapping:

                mapping[name] = {
                    "activity_type": ActivityType.OTHER,
                    "user_right_type": None
                }

        return mapping
