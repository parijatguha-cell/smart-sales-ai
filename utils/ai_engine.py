import os
import re
import json
import time
from dotenv import load_dotenv
from google import genai
from google.genai import errors

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODELS = ["gemini-3.8-flash"]


def ask_gemini(prompt: str) -> str:
    last_error = None
    for model in MODELS:
        for attempt in range(4):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                )
                return response.text
            except errors.ServerError as e:
                last_error = e
                time.sleep(2 * (attempt + 1))
    raise last_error


def generate_questions(setup: dict, count: int = 5) -> list:
    """Ask Gemini for customer questions and return them as a Python list."""
    prompt = f"""
You are a realistic customer in a sales roleplay. A salesperson is practicing their pitch.

Product or service details:
{setup['product_info'][:6000]}

Scenario type: {setup['scenario_type']}
Difficulty: {setup['difficulty']}

Write exactly {count} questions or objections that a real customer would say to the salesperson.
Make them specific to the product or service above. Match the scenario type and difficulty.

Return ONLY a JSON array of {count} strings. No extra text, no numbering, no markdown.
Example format: ["Question one?", "Question two?"]
"""
    text = ask_gemini(prompt)
    clean = re.sub(r"```json|```", "", text).strip()
    questions = json.loads(clean)
    return [str(q) for q in questions][:count]


def evaluate_answers(setup: dict, questions: list, answers: dict) -> dict:
    """Score each answer out of 20 and return a results dictionary."""
    results = []
    to_score = []

    for i, q in enumerate(questions):
        a = answers.get(i, "").strip()
        if a:
            to_score.append({"index": i, "question": q, "answer": a})
        else:
            results.append({
                "index": i,
                "question": q,
                "answer": "",
                "score": 0,
                "feedback": "No answer was given.",
                "missing": [],
            })

    if to_score:
        prompt = f"""
You are a strict but fair sales coach. A salesperson answered customer questions.

Product or service details:
{setup['product_info'][:4000]}

Scenario type: {setup['scenario_type']}
Difficulty: {setup['difficulty']}

Score each answer out of 20 using: relevance to the customer's concern (6),
product knowledge (5), persuasion and benefits (5), clarity and tone (4).

Items to score (JSON):
{json.dumps(to_score)}

Return ONLY a JSON array. One object per item, in the same order, with keys:
"index" (number), "score" (number 0-20), "feedback" (one or two sentences),
"missing" (array of short strings, points the salesperson should have covered).
No markdown, no extra text.
"""
        text = ask_gemini(prompt)
        clean = re.sub(r"```json|```", "", text).strip()
        scored = json.loads(clean)
        by_index = {s["index"]: s for s in scored}

        for item in to_score:
            s = by_index.get(item["index"], {})
            results.append({
                "index": item["index"],
                "question": item["question"],
                "answer": item["answer"],
                "score": max(0, min(20, int(s.get("score", 0)))),
                "feedback": s.get("feedback", ""),
                "missing": s.get("missing", []),
            })

    results.sort(key=lambda r: r["index"])
    total = sum(r["score"] for r in results)
    answered = sum(1 for r in results if r["answer"])

    summary_prompt = f"""
A salesperson scored {total}/{len(questions) * 20} in a {setup['scenario_type']} practice.
They answered {answered} of {len(questions)} questions.
Per-question feedback: {json.dumps([r['feedback'] for r in results])}
Write a short, encouraging overall feedback paragraph (3 to 4 sentences) with the main
strengths and what to improve. Plain text only.
"""
    overall = ask_gemini(summary_prompt).strip()

    return {
        "results": results,
        "total": total,
        "max": len(questions) * 20,
        "answered": answered,
        "overall": overall,
    }