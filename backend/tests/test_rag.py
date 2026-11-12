import numpy as np
import pytest
from fastapi.testclient import TestClient
from app.rag import Rag, read_chunks, focus_sampling_row
from app.main import app, rag


def test_documents_and_tables():
    chunks = read_chunks()
    assert len({(c['file'], c['page']) for c in chunks}) == 7
    assert not any(c['file'] == 'Sample_Questions.pdf' for c in chunks)
    old = next(c for c in chunks if c['revision'] == 3)
    assert not old['current']
    current = next(c for c in chunks if c['document'] == 'QC-SOP-014' and c['section'] == '4. Sampling Plan' and c['current'])
    assert '501 - 3,200' in current['text']
    assert '32' in current['text']
    assert 'Lot size (pieces): 501 - 3,200; Samples to inspect: 32' in current['text']
    focused = focus_sampling_row(current['text'], 'For a lot of 600 pieces with two minor defects?')
    assert 'Samples to inspect: 32' in focused
    assert 'Samples to inspect: 13' not in focused


def test_revision_filter_and_continuation(monkeypatch):
    engine = Rag()
    engine.chunks = read_chunks()
    engine.vectors = np.ones((len(engine.chunks), 2)) / np.sqrt(2)
    monkeypatch.setattr(engine, 'embed', lambda texts: np.array([[1., 0.]]))
    current = engine.retrieve('QC-SOP-014 sampling plan')
    assert all(c['current'] for c in current)
    continuation = engine.retrieve('Removal of a Lock When the Owner Is Absent')
    assert {c['page'] for c in continuation if c['section'].startswith('6. Removal')} == {1, 2}
    history = engine.retrieve('Rev 03 paper QF-07 Red Bin', True)
    assert any(c['revision'] == 3 for c in history)


def test_api_validation_and_source_allowlist(monkeypatch):
    monkeypatch.setattr(rag, 'chunks', read_chunks())
    client = TestClient(app)
    assert client.post('/api/ask', json={'question': ' '}).status_code == 422
    assert client.get('/api/documents/unknown.pdf').status_code == 404
    assert client.get('/api/documents/QC-SOP-014_Rev04_Incoming_Material_Inspection.pdf').headers['content-type'] == 'application/pdf'


@pytest.mark.parametrize('size,samples', [(5,'All pieces'), (6,'5'), (90,'5'), (91,'13'), (500,'13'), (501,'32'), (3200,'32'), (3201,'50')])
def test_sampling_boundaries(size, samples):
    chunk = next(c for c in read_chunks() if c['section'] == '4. Sampling Plan')
    text = focus_sampling_row(chunk['text'], f'For a lot of {size} pieces?')
    rows = [line for line in text.splitlines() if line.startswith('Lot size (pieces):')]
    assert len(rows) == 1
    assert f'Samples to inspect: {samples};' in rows[0]
