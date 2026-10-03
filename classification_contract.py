"""Validated ingestion contract: legacy fields plus complete conservative taxonomy."""
from taxonomy import validate_taxonomy

CATEGORIES = ('ads', 'advice', 'before-and-after', 'business-ideas', 'copywriting', 'data',
              'direct-mail', 'emails', 'images', 'money', 'motivation', 'pricing',
              'print-ads', 'quotes', 'sales-pages', 'social', 'swipes-email',
              'testimonials', 'videos', 'wisdom')
TEXT_FIELDS = ('title', 'description', 'framework', 'hook', 'mechanism', 'cta',
               'why_it_works', 'adaptation')
LIST_FIELDS = ('objective', 'emotion', 'tone', 'tags')
VOCABULARIES = {
 'record_type': ('real_piece', 'template', 'framework', 'guidance', 'collection'),
 'channel': ('email', 'social', 'web', 'direct_mail', 'print', 'outdoor', 'messaging', 'multichannel'),
 'platform': ('instagram', 'facebook', 'linkedin', 'youtube', 'tiktok', 'whatsapp', 'sms'),
 'format': ('static_ad', 'print_ad', 'postcard', 'letter', 'reel', 'short_video', 'video',
            'carousel', 'email', 'email_sequence', 'subject_line', 'landing_page',
            'product_page', 'pricing_page', 'case_study', 'message', 'curated_list',
            'static_image', 'short_phrase', 'generic_ad'),
 'distribution': ('paid', 'organic', 'owned'),
 'lifecycle_function': ('acquisition', 'conversion', 'retention', 'reactivation', 'advocacy'),
 'decision_stage': ('awareness', 'consideration', 'decision', 'post_purchase'),
 'strategic_jobs': ('introduce_product', 'explain_value', 'make_benefits_scannable',
    'clarify_promise', 'show_transformation', 'surface_cost_of_inaction', 'overcome_objection',
    'reduce_action_friction', 'interrupt_attention', 'humanize_brand', 'drive_event_attendance',
    'signal_identity', 'differentiate', 'build_desire', 'nurture_interest', 'build_trust',
    'advance_decision', 'challenge_belief', 'reframe_problem', 'personalize_message',
    'clarify_offer', 'earn_open', 'stimulate_curiosity', 'communicate_visually',
    'explain_economic_value', 'activate_aspiration', 'build_identification', 'justify_price',
    'anchor_value', 'clarify_message', 'make_message_memorable', 'anticipate_experience',
    'educate', 'help_reference_discovery', 'reduce_uncertainty', 'sustain_attention',
    'deliver_payoff', 'connect_brand_meaning', 'restore_relationship', 'encourage_repeat_purchase',
    'support_product_usage', 'recognize_customer', 'qualify_lead', 'reduce_risk'),
 'proof_types': ('testimonial', 'social_proof', 'before_after', 'demonstration',
                 'quantified_benefit', 'data_evidence', 'case_study', 'expert_authority', 'none'),
 'proof_status': ('recommended_only', 'reported_in_source', 'observed_in_asset', 'none'),
 'proof_verification': ('unverified',),
 'audience_relationship': ('prospect', 'lead', 'active_customer', 'lapsed_customer', 'subscriber'),
 'conversion_action': ('purchase', 'request_quote', 'book_call', 'visit_event', 'reply',
    'subscribe', 'return_purchase', 'try_product', 'open_email', 'share', 'visit_site',
    'use_product', 'renew'),
 'offer_type': ('product', 'service', 'event', 'content', 'subscription', 'real_estate_service'),
 'next_step_offer': ('free_quote', 'free_assessment', 'trial', 'event', 'consultation', 'content'),
 'incentive_type': ('discount', 'free_quote', 'free_assessment', 'bonus', 'free_trial', 'none'),
 'framework_codes': ('aida', 'bab', 'pas', 'fab', '4ps', 'problem_solution'),
 'technique_codes': ('contrarian_hook', 'curiosity_gap', 'knowledge_gap', 'price_anchoring',
    'sensory_desire', 'social_proof', 'contrast', 'data_hook', 'visual_hook', 'cost_per_day',
    'loss_aversion', 'comparison', 'risk_reversal', 'personalization'),
 'pattern_codes': ('headline_body_cta', 'direct_response', 'hook_retention_payoff'),
}
ARRAY_FIELDS = {'lifecycle_function', 'decision_stage', 'strategic_jobs', 'proof_types',
                'framework_codes', 'technique_codes', 'pattern_codes'}


def validate_classification(data):
    if not isinstance(data, dict) or data.get('category') not in CATEGORIES:
        raise ValueError('Categoria de classificação inválida')
    for field in TEXT_FIELDS:
        value = data.get(field)
        if not isinstance(value, str) or len(value) > 2000:
            raise ValueError('Campo textual de classificação inválido')
    if not data['title'].strip() or not data['description'].strip():
        raise ValueError('Classificação sem título ou descrição')
    for field in LIST_FIELDS:
        value = data.get(field)
        if not isinstance(value, list) or len(value) > 10 or any(
                not isinstance(x, str) or not x.strip() or len(x) > 300 for x in value):
            raise ValueError('Lista de classificação inválida')
    taxonomy = validate_taxonomy(data.get('taxonomy'))
    attrs = taxonomy['attributes']
    for field, attr in attrs.items():
        value = attr['value']
        if len(attr['evidence']) > 400:
            raise ValueError('Evidência deve ser breve')
        if value in ('unknown', 'not_applicable'):
            if attr['certainty'] != value or attr['application'] != value:
                raise ValueError('Estado desconhecido/não aplicável inconsistente')
            if attr['evidence_origin'] != 'none':
                raise ValueError('Ausência de evidência deve ser explícita')
            continue
        if attr['evidence_origin'] == 'original_asset':
            raise ValueError('Pipeline textual não inspeciona assets originais')
        if attr['certainty'] == 'observed' and attr['evidence_origin'] not in ('source_description', 'stored_template'):
            raise ValueError('Observação deve identificar fonte')
        if attr['certainty'] == 'inferred' and attr['evidence_origin'] != 'analyst_interpretation':
            raise ValueError('Inferência deve identificar interpretação')
        if field in VOCABULARIES:
            values = value if isinstance(value, list) else [value]
            if (field in ARRAY_FIELDS) != isinstance(value, list) or not 1 <= len(values) <= 8:
                raise ValueError('Tipo ou tamanho de atributo inválido')
            if any(not isinstance(x, str) or x not in VOCABULARIES[field] for x in values):
                raise ValueError('Vocabulário de atributo inválido')
        elif field == 'strategic_summary':
            if not isinstance(value, str) or not 1 <= len(value) <= 1000:
                raise ValueError('Resumo estratégico inválido')
        elif field == 'market_context':
            if not isinstance(value, dict) or not value or not set(value) <= {
                    'sector', 'brand', 'business_model', 'geography', 'topic'}:
                raise ValueError('Contexto de mercado inválido')
            if any(not isinstance(x, str) or len(x) > 150 for x in value.values()):
                raise ValueError('Contexto de mercado inválido')
        else:
            raise ValueError('Atributo inválido')
    kind = attrs['record_type']['value']
    if kind == 'unknown' or attrs['strategic_summary']['value'] == 'unknown':
        raise ValueError('Tipo e resumo estratégico são obrigatórios')
    for field in ('proof_types', 'framework_codes', 'technique_codes', 'pattern_codes', 'strategic_jobs'):
        attr = attrs[field]
        if attr['value'] not in ('unknown', 'not_applicable'):
            expected = 'present' if kind in ('real_piece', 'collection') else 'recommended'
            if attr['application'] != expected:
                raise ValueError('Técnica recomendada versus presente inconsistente')
    status = attrs['proof_status']['value']
    if kind != 'real_piece' and status in ('reported_in_source', 'observed_in_asset'):
        raise ValueError('Template não contém prova executada')
    if status == 'observed_in_asset':
        raise ValueError('Prova não inspecionada diretamente')
    if attrs['proof_types']['value'] not in ('unknown', 'not_applicable', ['none']):
        if status != ('reported_in_source' if kind == 'real_piece' else 'recommended_only'):
            raise ValueError('Status de prova inconsistente')
    if kind == 'real_piece' and status == 'recommended_only':
        raise ValueError('Recomendação não é prova presente')
    lifecycle = attrs['lifecycle_function']['value']
    relation = attrs['audience_relationship']['value']
    if isinstance(lifecycle, list):
        if 'retention' in lifecycle and relation != 'active_customer':
            raise ValueError('Retenção requer evidência de cliente ativo')
        if 'reactivation' in lifecycle and relation != 'lapsed_customer':
            raise ValueError('Reativação requer evidência de cliente inativo')
    return data
