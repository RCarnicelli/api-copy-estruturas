"""Offline test data; never ingested or used as an operational swipe source."""
from taxonomy import unknown_taxonomy


def classification_fixture(url='https://swipefile.com/example'):
    data = {key: 'Example' for key in ('title', 'description', 'framework', 'hook',
                                      'mechanism', 'cta', 'why_it_works', 'adaptation')}
    data.update(category='ads', objective=['vender'], emotion=['desejo'], tone=['direto'],
                tags=['teste'], source_url=url, taxonomy=unknown_taxonomy())
    data['taxonomy']['attributes']['record_type'] = {
        'value': 'real_piece', 'certainty': 'observed', 'application': 'not_applicable',
        'evidence_origin': 'source_description', 'evidence': 'Fonte descreve anúncio específico.'}
    data['taxonomy']['attributes']['strategic_summary'] = {
        'value': 'Anúncio de teste de classificação.', 'certainty': 'inferred', 'application': 'present',
        'evidence_origin': 'analyst_interpretation', 'evidence': 'Interpretação do exemplo.'}
    return data
