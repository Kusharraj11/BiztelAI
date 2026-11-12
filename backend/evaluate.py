"""Run real-model checks and save reviewable responses, not just pass/fail assertions."""
import json
import time
from pathlib import Path
import httpx

CASES = [
    ('What is the recommended coolant concentration for the TX-200 CNC turning centre?', ['6', '8'], False),
    ('The machine is showing alarm AL-104. What does it mean and what should the operator do?', ['68', 'reset'], False),
    ('Who is allowed to remove a lockout lock from a machine?', ['own', 'production manager', 'safety officer'], False),
    ('What is the outer diameter tolerance for the BH-220 bearing housing?', ['0.05'], False),
    ('How often should spindle runout be checked, and who does it?', ['monthly', 'maintenance'], False),
    ('For a lot of 600 pieces with two minor defects and no other defects, how many samples are required and is it accepted?', ['32', 'reject'], False),
    ('Can we inspect or accept a lot when the supplier MTC is missing?', ['hold'], False),
    ('Where should rejected material go, who holds the key, and how soon must SQE be informed?', ['q1', '3', 'supervisor', '4'], False),
    ('Compare Rev 03 and Rev 04: what changed in incoming inspection record forms and retention?', ['qf-07', 'qf-07a', '2 years', '5 years'], True),
    ('What is the recommended spindle bearing replacement interval in hours for the TX-200?', [], False),
]

if __name__ == '__main__':
    results = []
    with httpx.Client(timeout=300) as client:
        for question, expected, history in CASES:
            start = time.monotonic()
            response = client.post('http://127.0.0.1:8000/api/ask', json={'question': question, 'include_history': history})
            response.raise_for_status()
            data = response.json()
            passed = all(word in data['answer'].lower() for word in expected) and bool(data['sources']) if expected else not data['found']
            results.append(dict(question=question, history=history, seconds=round(time.monotonic()-start, 2), keyword_check=passed, **data))
            print(len(results), passed, data['answer'], flush=True)
            Path('evaluation-results.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
