# 🧠 Lightweight Entity Extraction Module
# Uses regex patterns for fast entity detection

import logging
import re

# 🛠️ Logger Setup
logger = logging.getLogger(__name__)

# 📦 Lightweight regex patterns for entity extraction
NAME_PATTERNS = [
    r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',  # First Last
    r'\b[A-Z]\. [A-Z][a-z]+\b',      # F. Last
    r'\b[A-Z][a-z]+ [A-Z]\. [A-Z][a-z]+\b'  # First M. Last
]

ORG_PATTERNS = [
    r'\b[A-Z][a-zA-Z\s]*(?:Company|Corp|Inc|Ltd|LLC|Center|Institute|University|Association)\b',
    r'\b(?:Company|Corp|Inc|Ltd|LLC) [A-Z][a-zA-Z\s]*\b'
]

LOC_PATTERNS = [
    r'\b[A-Z][a-z]+,\s*[A-Z][a-z]+\b',  # City, State
    r'\b[A-Z][a-z]+,\s*[A-Z]{2}\b'      # City, ST
]

MISC_PATTERNS = [
    r'\b\d{1,2}/\d{1,2}/\d{4}\b',       # Dates
    r'\b[A-Z][a-z]+\s+\d{1,2},\s+\d{4}\b',  # Month DD, YYYY
    r'\b\d{4,}\b',                      # Numbers
    r'#\d{4}-\d{2}',                    # Project codes
    r'\b\d+\s*%\b'                      # Percentages
]

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
    🏷️ Extract entities using lightweight regex patterns.
    """
    logger.info(f"Starting extraction for: {document_type}")
    
    entities = {}
    
    # Extract names
    names = []
    for pattern in NAME_PATTERNS:
        names.extend(re.findall(pattern, content))
    if names:
        entities['PER'] = list(set(names))[:5]
    
    # Extract organizations
    orgs = []
    for pattern in ORG_PATTERNS:
        orgs.extend(re.findall(pattern, content, re.IGNORECASE))
    if orgs:
        entities['ORG'] = list(set(orgs))[:5]
    
    # Extract locations
    locs = []
    for pattern in LOC_PATTERNS:
        locs.extend(re.findall(pattern, content))
    if locs:
        entities['LOC'] = list(set(locs))[:5]
    
    # Extract miscellaneous
    misc = []
    for pattern in MISC_PATTERNS:
        misc.extend(re.findall(pattern, content))
    if misc:
        entities['MISC'] = list(set(misc))[:10]
    
    return _apply_mapping(entities, document_type)

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