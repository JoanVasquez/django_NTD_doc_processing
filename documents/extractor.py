# 🧠 Entity Extraction Module
# Combines Regex, HuggingFace NER, and Proper-Noun fallback for robust entity detection

import logging
import re
from transformers import pipeline
import nltk
from nltk import ne_chunk, pos_tag, word_tokenize
from nltk.corpus import words, stopwords
from nltk.metrics import edit_distance

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('averaged_perceptron_tagger')
try:
    nltk.data.find('chunkers/maxent_ne_chunker')
except LookupError:
    nltk.download('maxent_ne_chunker')
try:
    nltk.data.find('corpora/words')
except LookupError:
    nltk.download('words')

# Load word list for spell correction
word_list = set(words.words())


# 🛠️ Logger Setup
logger = logging.getLogger(__name__)


# 📦 Lazy-loaded NER Pipeline
ner_pipeline = None
def get_ner_pipeline():
    """
    ⚙️ Lazily initialize and return a HuggingFace NER pipeline.
    """
    global ner_pipeline
    if ner_pipeline is None:
        ner_pipeline = pipeline(
            "token-classification",
            model="dslim/bert-base-NER",
            aggregation_strategy="simple"
        )
    return ner_pipeline


# 🗂️ Domain-specific Entity Mapping
ENTITY_MAPPING = {
    "advertisement": {"ORG": "advertiser",      "PER": "contact_person",    "LOC": "target_location",    "MISC": "promotion_details"},
    "budget":        {"ORG": "budget_owner",    "MISC": "budget_code"},
    "email":         {"PER": "sender_or_receiver", "ORG": "company",     "LOC": "location",      "MISC": "reference_number"},
    "file_folder":   {"ORG": "folder_owner",    "MISC": "folder_id"},
    "form":          {"PER": "applicant_name",  "ORG": "organization",  "LOC": "submission_location"},
    "handwritten":   {"PER": "author",          "MISC": "notes"},
    "invoice":       {"ORG": "vendor",         "PER": "contact_person",    "LOC": "billing_location",    "MISC": "invoice_number"},
    "letter":        {"PER": "recipient",       "ORG": "sender_organization", "LOC": "address"},
    "memo":          {"PER": "author",          "ORG": "department",     "MISC": "subject"},
    "news_article":  {"PER": "journalist",      "ORG": "publisher",      "LOC": "location"},
    "presentation":  {"PER": "presenter",       "ORG": "organization"},
    "questionnaire": {"PER": "respondent",      "ORG": "survey_company"},
    "resume":        {"PER": "candidate_name",  "ORG": "company",       "LOC": "location"},
    "scientific_publication": {"PER": "author",  "ORG": "institution", "LOC": "research_location"},
    "scientific_report":      {"PER": "researcher", "ORG": "institution", "LOC": "report_location"},
    "specification":{"ORG": "issuing_organization", "MISC": "specification_id"}
}


def extract_entities(document_type: str, content: str) -> dict:
    """
    🏷️ Top-level dispatch to type-specific extraction.
    Applies proper-noun fallback if no entities found.

    Args:
        document_type: Name of the document category.
        content: Full text to analyze.

    Returns:
        Mapped entity dictionary.
    """
    logger.info(f"Starting extraction for: {document_type}")

    if document_type == 'news_article':
        raw = extract_news_article_entities(content)
    elif document_type in {'letter','form','memo','invoice','email'}:
        raw = extract_business_document_entities(content)
    else:
        raw = extract_generic_entities(content)

    # Enhanced fallback for noisy OCR text
    if not raw or all(not v for v in raw.values()):
        logger.info("No matches found; applying fallback extraction.")
        # Simple fallback - extract any words that look like entities
        words = re.findall(r'\b[A-Za-z]{3,}\b', content)
        names = re.findall(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', content)
        numbers = re.findall(r'\b\d{4,}\b', content)
        
        raw = {}
        if names:
            raw['PER'] = names[:5]
        if numbers:
            raw['MISC'] = numbers[:5]
        if not raw and words:
            # Last resort - just extract readable words
            clean_words = [w for w in words if len(w) >= 4][:10]
            raw = {'MISC': clean_words}
        
        logger.info(f"Fallback extracted: {raw}")

    return _apply_mapping(raw, document_type)


def extract_entities_nltk(content: str) -> dict:
    """Extract entities using NLTK NER and spell correction"""
    entities = {}
    
    try:
        # Tokenize and correct spelling
        tokens = word_tokenize(content)
        corrected_tokens = []
        
        for token in tokens:
            if len(token) > 2 and token.isalpha():
                # Simple spell correction for common OCR errors
                if token.lower() not in word_list:
                    candidates = [w for w in word_list if abs(len(w) - len(token)) <= 2]
                    if candidates:
                        closest = min(candidates, key=lambda x: edit_distance(token.lower(), x))
                        if edit_distance(token.lower(), closest) <= 2:
                            token = closest
                corrected_tokens.append(token)
            else:
                corrected_tokens.append(token)
        
        # POS tagging and NER
        pos_tags = pos_tag(corrected_tokens)
        named_entities = ne_chunk(pos_tags)
        
        # Extract entities from NLTK tree
        for chunk in named_entities:
            if hasattr(chunk, 'label'):
                entity_name = ' '.join([token for token, pos in chunk.leaves()])
                label = chunk.label()
                
                if label == 'PERSON':
                    entities.setdefault('PER', []).append(entity_name)
                elif label == 'ORGANIZATION':
                    entities.setdefault('ORG', []).append(entity_name)
                elif label in ['GPE', 'LOCATION']:
                    entities.setdefault('LOC', []).append(entity_name)
                else:
                    entities.setdefault('MISC', []).append(entity_name)
        
        # Deduplicate
        for key in entities:
            entities[key] = list(set(entities[key]))
            
    except Exception as e:
        logger.warning(f"NLTK extraction error: {e}")
    
    return entities


# ── Type-Specific Extractors ─────────────────────────────────────────────────

def extract_news_article_entities(content: str) -> dict:
    """
    Extracts entities most relevant to news articles (authors, locations, orgs, dates, stats).
    Always merges in NER results.
    """
    entities = {}
    
    # Authors (usually at end in ALL CAPS)
    authors = re.findall(r'^([A-Z][A-Z\s]+)$', content, re.MULTILINE)
    if authors:
        entities['PER'] = [author.strip() for author in authors]
    
    # Organizations/institutions
    orgs = re.findall(r'\b(?:University of [A-Z][a-z]+|[A-Z][a-z]+\s+(?:Association|University|Institute|Company))\b', content)
    if orgs:
        entities['ORG'] = orgs
    
    # Dates with day names
    dates = re.findall(r'\b(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),\s+[A-Z][a-z]+\s+\d{1,2},\s+\d{4}\b', content)
    if dates:
        entities['MISC'] = entities.get('MISC', []) + dates
    
    # Statistics and percentages
    stats = re.findall(r'\b\d+\s*percent\b|\b\d+%\b', content, re.IGNORECASE)
    if stats:
        entities['MISC'] = entities.get('MISC', []) + stats
    
    # Locations (cities, states)
    locations = re.findall(r'\b[A-Z][a-z]+,\s*[A-Z][a-z]+\b', content)
    if locations:
        entities['LOC'] = locations
    
    return _merge_ner(content, entities)


def extract_business_document_entities(content: str) -> dict:
    """
    Extracts entities from forms, letters, memos, invoices, emails.
    """
    entities = {}
    
    # Names (various patterns)
    name_patterns = [
        r'\b[A-Z]\. [A-Z][a-z]+\b',
        r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',
        r'\b[A-Z]\. [A-Z]\. [A-Z][a-z]+\b',
        r'\b[A-Z][a-z]+ [A-Z]\. [A-Z][a-z]+\b'
    ]
    names = []
    for pattern in name_patterns:
        names.extend(re.findall(pattern, content))
    if names:
        entities['PER'] = names
    
    # Organizations
    org_patterns = [
        r'\b[A-Z][a-zA-Z\s]*(?:company|corp|inc|ltd|center)\b',
        r'\bDevelopment Center\b',
        r'\b[A-Z][a-zA-Z]+\s+(?:Company|Corp|Inc|Ltd)\b'
    ]
    orgs = []
    for pattern in org_patterns:
        orgs.extend(re.findall(pattern, content, re.IGNORECASE))
    if orgs:
        entities['ORG'] = [org.strip() for org in orgs]
    
    # Locations
    locations = re.findall(r'\b[A-Z][a-z]+,\s*[A-Z][a-z]+\b', content)
    if locations:
        entities['LOC'] = locations
    
    # Project numbers, codes, quantities
    misc_items = []
    projects = re.findall(r'#\d{4}-\d{2}|PROJECT\s+#\d{4}-\d{2}', content, re.IGNORECASE)
    misc_items.extend(projects)
    
    codes = re.findall(r'\b\d{6}\b', content)
    misc_items.extend(codes)
    
    quantities = re.findall(r'\b\d+\s+cartons?\b', content, re.IGNORECASE)
    misc_items.extend(quantities)
    
    if misc_items:
        entities['MISC'] = misc_items
    
    return _merge_ner(content, entities)


def extract_generic_entities(content: str) -> dict:
    """
    Generic fallback extractor using broad regex for PER, ORG, LOC, MISC.
    """
    entities = {}
    
    # Generic name patterns
    names = re.findall(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', content)
    if names:
        entities['PER'] = names[:10]  # Limit to avoid noise
    
    # Generic organization patterns
    orgs = re.findall(r'\b[A-Z][a-zA-Z\s]*(?:company|corp|inc|ltd|center|association|university|institute)\b', content, re.IGNORECASE)
    if orgs:
        entities['ORG'] = [org.strip() for org in orgs[:5]]
    
    # Generic location patterns
    locations = re.findall(r'\b[A-Z][a-z]+,\s*[A-Z][a-z]+\b', content)
    if locations:
        entities['LOC'] = locations[:5]
    
    # Generic miscellaneous (dates, numbers, codes)
    misc_items = []
    dates = re.findall(r'\b\d{1,2}/\d{1,2}/\d{4}\b|\b[A-Z][a-z]+\s+\d{1,2},\s+\d{4}\b', content)
    misc_items.extend(dates)
    
    numbers = re.findall(r'\b\d{4,}\b', content)
    misc_items.extend(numbers[:5])
    
    if misc_items:
        entities['MISC'] = misc_items
    
    return _merge_ner(content, entities)


# ── Core Helpers ────────────────────────────────────────────────────────────────

def _merge_ner(content: str, entities: dict) -> dict:
    """
    ⚡ Merge in HuggingFace NER results to existing entities.
    Deduplicates all values.
    """
    try:
        ner = get_ner_pipeline()
        for item in ner(content):
            tag  = item['entity_group']
            word = item['word'].strip()
            entities.setdefault(tag, []).append(word)
    except Exception as e:
        logger.warning(f"NER pipeline error: {e}")

    # Dedupe
    for t, vals in list(entities.items()):
        entities[t] = list(set(vals))
    return entities


def _apply_mapping(entities: dict, document_type: str) -> dict:
    """
    🗺️ Map raw tags (PER/ORG/LOC/MISC) to domain-specific field names.
    """
    mapping = ENTITY_MAPPING.get(document_type, {})
    mapped = {}
    for tag, vals in entities.items():
        key = mapping.get(tag, tag)
        mapped[key] = vals

    logger.info(f"Final entities for {document_type}: {mapped}")
    return mapped


def extract_generic_entities(content: str) -> dict:
    """
    Generic fallback extractor using broad regex for PER, ORG, LOC, MISC.
    """
    entities = {}
    # Generic regex blocks for names, orgs, locs, dates, projects
    # … (regex code omitted for brevity) …
    return _merge_ner(content, entities)


# ── Core Helpers ────────────────────────────────────────────────────────────────

def _merge_ner(content: str, entities: dict) -> dict:
    """
    ⚡ Merge in HuggingFace NER results to existing entities.
    Deduplicates all values.
    """
    try:
        ner = get_ner_pipeline()
        for item in ner(content):
            tag  = item['entity_group']
            word = item['word'].strip()
            entities.setdefault(tag, []).append(word)
    except Exception as e:
        logger.warning(f"NER pipeline error: {e}")

    # Dedupe
    for t, vals in list(entities.items()):
        entities[t] = list(set(vals))
    return entities


def _apply_mapping(entities: dict, document_type: str) -> dict:
    """
    🗺️ Map raw tags (PER/ORG/LOC/MISC) to domain-specific field names.
    """
    mapping = ENTITY_MAPPING.get(document_type, {})
    mapped = {}
    for tag, vals in entities.items():
        key = mapping.get(tag, tag)
        mapped[key] = vals

    logger.info(f"Final entities for {document_type}: {mapped}")
    return mapped
