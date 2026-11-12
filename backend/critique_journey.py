"""Record a real, reproducible local AI critique of the disclosed assisted journey."""
import json
from pathlib import Path
import httpx

root = Path(__file__).resolve().parent.parent
thinking = (root / 'THINKING.md').read_text(encoding='utf-8')
journey = thinking.split('### Proposed journey\n', 1)[1].split('## AI challenge', 1)[0]
prompt = ('Act as a skeptical shop-floor supervisor and product manager. Critique this AI-assisted journey. '
          'The applicant has not provided an independent pre-AI draft; do not pretend otherwise. '
          'Give four concrete risks and four practical changes. Focus on mobile use, source trust, '
          'unclear questions, safety exceptions, revision control and failed connectivity. '
          'Keep your response under 350 words.\n\n' + journey)
response = httpx.post('http://127.0.0.1:11434/api/chat', json={
    'model': 'qwen3:4b', 'think': False, 'stream': False,
    'options': {'temperature': 0, 'num_ctx': 4096, 'num_predict': 1024},
    'messages': [{'role': 'user', 'content': prompt}],
}, timeout=240)
response.raise_for_status()
answer = response.json()['message']['content']
answer = answer.split('</think>')[-1].strip()
answer = answer.split('**Why this works on the floor**')[0].strip()
(root / 'AI_CHALLENGE.md').write_text(
    '# Actual AI journey critique\n\nTool: local Ollama, qwen3:4b. Recorded 12 November 2026. '
    'The supplied journey was AI-assisted, not an independently written initial draft.\n\n'
    '## Prompt sent\n\n' + prompt + '\n\n## Actual response excerpts\n\n' + answer + '\n', encoding='utf-8')
print(answer)
