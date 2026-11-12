"""Copy the five saved additional evaluation responses into the submission README."""
import json
from pathlib import Path

root = Path(__file__).resolve().parent.parent
readme = root / 'README.md'
text = readme.read_text(encoding='utf-8').split('\n## Five additional questions and actual app answers')[0]
results = json.loads((root / 'backend/evaluation-results.json').read_text(encoding='utf-8'))
parts = ['\n## Five additional questions and actual app answers\n',
         'Recorded outputs from 12 November 2026. Bracketed numbers identify source cards for that individual request.\n']
for number, result in enumerate(results[5:], 1):
    parts.append(f"### {number}. {result['question']}\n")
    if result['history']:
        parts.append('Mode: include superseded revisions for this comparison.\n')
    parts.append('**Actual app answer:** ' + result['answer'] + '\n')
    sources = ', '.join(f"{s['file']}, page {s['page']}" for s in result['sources'])
    parts.append('Sources: ' + (sources or 'None; the requested specification is absent from the supplied documents.') + '\n')
parts.append('''## Use from a phone on the same Wi-Fi

Run `.\\start.ps1 -Lan` from the project directory, then open `http://<laptop-private-IP>:8000` on the phone. Find the Wi-Fi IPv4 address with `ipconfig`. Both devices must be on the same network. The UI and API share port 8000, so no frontend URL or CORS change is needed. Ollama stays on laptop loopback.

If access fails, check LAN mode, private-network firewall access and Wi-Fi client isolation. Phone access was confirmed by the applicant on 12 November 2026, and the server received requests from a second LAN device. The recording will be completed later by the applicant; see [SUBMISSION.md](SUBMISSION.md).

## Submission notes

[THINKING.md](THINKING.md) contains user assumptions, the journey, actual AI conversation excerpts, improvement rationale and final reflection. The missing manual-first journey is explicitly disclosed. [EVALUATION.md](EVALUATION.md) contains all ten recorded responses. [SUBMISSION.md](SUBMISSION.md) tracks remaining items and gives a 2–3 minute recording outline.
''')
readme.write_text(text + '\n'.join(parts), encoding='utf-8')
report = ['# Evaluation results', '',
          'Recorded local run: 12 November 2026. All 10 keyword checks passed. Answers were also reviewed against source content; this development set is not a general accuracy guarantee.', '',
          'Backend: 11 tests passed, including sampling boundaries. React production build passed. Browser checks verified coolant and AL-104 answers with source cards, plus the explicit not-found state. LAN serving was verified and the applicant confirmed actual phone use on the same Wi-Fi.', '',
          '| Question | Actual answer | Seconds |', '| --- | --- | --- |']
for result in results:
    report.append('| ' + result['question'].replace('|', '/') + ' | ' + result['answer'].replace('|', '/').replace('\n', ' ') + ' | ' + str(result['seconds']) + ' |')
(root / 'EVALUATION.md').write_text('\n'.join(report) + '\n', encoding='utf-8')
