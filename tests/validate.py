import json

final = [json.loads(l) for l in open("data/query_logs_final.jsonl")]
answers = {json.loads(l)["query_id"] for l in open("data/clarification_answers.jsonl")}

missing_core = 0
unresolved = 0

for r in final:
    if not r.get("time_range") or not r.get("intent"):
        missing_core += 1

    if r.get("clarification_resolved") and r["query_id"] not in answers:
        unresolved += 1

print("records missing core fields:", missing_core)
print("resolved but no answers:", unresolved)