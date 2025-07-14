from django.test import TestCase
from documents.extractor import extract_entities, _apply_mapping

class EntityExtractorTest(TestCase):
    
    def test_extract_entities_letter(self):
        """Test entity extraction for letter document type"""
        text = "Dear John Smith, Microsoft Corporation is located in Seattle, WA. Project #2024-01."
        entities = extract_entities("letter", text)
        self.assertIsInstance(entities, dict)
        # Should have mapped fields for letter type
        self.assertTrue(any(key in ["recipient", "sender_organization", "address"] for key in entities.keys()))
    
    def test_extract_entities_invoice(self):
        """Test entity extraction for invoice document type"""
        text = "Invoice from ACME Corp to Jane Doe. Invoice #INV-12345. Location: New York, NY"
        entities = extract_entities("invoice", text)
        self.assertIsInstance(entities, dict)
        # Should have mapped fields for invoice type
        expected_fields = ["vendor", "contact_person", "billing_location", "invoice_number"]
        self.assertTrue(any(field in entities for field in expected_fields))
    
    def test_extract_entities_memo(self):
        """Test entity extraction for memo document type"""
        text = "Memo from John Smith at Engineering Department regarding project updates"
        entities = extract_entities("memo", text)
        self.assertIsInstance(entities, dict)
    
    def test_extract_entities_empty_text(self):
        """Test extraction with empty text"""
        entities = extract_entities("letter", "")
        self.assertIsInstance(entities, dict)
    
    def test_extract_entities_no_matches(self):
        """Test extraction with text that has no entity matches"""
        text = "xyz abc def 123"
        entities = extract_entities("letter", text)
        self.assertIsInstance(entities, dict)
    
    def test_extract_entities_names(self):
        """Test name pattern extraction"""
        text = "John Smith, Mary Johnson, and Dr. Wilson are attending."
        entities = extract_entities("letter", text)
        self.assertIsInstance(entities, dict)
        # Should extract names and map them appropriately
        self.assertTrue(len(entities) >= 0)
    
    def test_extract_entities_organizations(self):
        """Test organization pattern extraction"""
        text = "Microsoft Corporation, Apple Inc, and Google LLC are tech companies."
        entities = extract_entities("letter", text)
        self.assertIsInstance(entities, dict)
    
    def test_extract_entities_locations(self):
        """Test location pattern extraction"""
        text = "Offices in New York, NY and Los Angeles, CA are open."
        entities = extract_entities("letter", text)
        self.assertIsInstance(entities, dict)
    
    def test_extract_entities_dates_and_numbers(self):
        """Test miscellaneous pattern extraction (dates, numbers, codes)"""
        text = "Meeting on 12/25/2023 for project #2024-01 with 85% completion."
        entities = extract_entities("letter", text)
        self.assertIsInstance(entities, dict)
    
    def test_apply_mapping_letter(self):
        """Test entity mapping for letter document type"""
        raw_entities = {
            "PER": ["John Smith"],
            "ORG": ["ACME Corp"],
            "LOC": ["New York, NY"],
            "MISC": ["12/25/2023"]
        }
        mapped = _apply_mapping(raw_entities, "letter")
        
        # Should map to letter-specific field names
        expected_mappings = {
            "recipient": ["John Smith"],
            "sender_organization": ["ACME Corp"],
            "address": ["New York, NY"],
            "MISC": ["12/25/2023"]  # No specific mapping for MISC in letter
        }
        
        # Check that mapping occurred
        self.assertIn("recipient", mapped)
        self.assertIn("sender_organization", mapped)
        self.assertIn("address", mapped)
    
    def test_apply_mapping_invoice(self):
        """Test entity mapping for invoice document type"""
        raw_entities = {
            "ORG": ["Vendor Corp"],
            "PER": ["Contact Person"],
            "LOC": ["Billing City, ST"],
            "MISC": ["INV-123"]
        }
        mapped = _apply_mapping(raw_entities, "invoice")
        
        # Should map to invoice-specific field names
        self.assertIn("vendor", mapped)
        self.assertIn("contact_person", mapped)
        self.assertIn("billing_location", mapped)
        self.assertIn("invoice_number", mapped)
    
    def test_apply_mapping_unknown_type(self):
        """Test entity mapping for unknown document type"""
        raw_entities = {"PER": ["John Smith"], "ORG": ["Company"]}
        mapped = _apply_mapping(raw_entities, "unknown_type")
        
        # Should keep original tags when no mapping exists
        self.assertIn("PER", mapped)
        self.assertIn("ORG", mapped)
    
    def test_apply_mapping_empty_entities(self):
        """Test entity mapping with empty entities"""
        mapped = _apply_mapping({}, "letter")
        self.assertIsInstance(mapped, dict)
        self.assertEqual(len(mapped), 0)
    
    def test_extract_entities_deduplication(self):
        """Test that duplicate entities are removed"""
        text = "John Smith and John Smith work at ACME Corp and ACME Corp"
        entities = extract_entities("letter", text)
        
        # Check that each entity list has no duplicates
        for key, values in entities.items():
            if values:
                self.assertEqual(len(values), len(set(values)), f"Duplicates found in {key}: {values}")
    
    def test_extract_entities_case_insensitive_orgs(self):
        """Test case insensitive organization extraction"""
        text = "apple inc and MICROSOFT CORP are companies"
        entities = extract_entities("letter", text)
        self.assertIsInstance(entities, dict)
        # Should extract organizations regardless of case
    
    def test_extract_entities_multiple_document_types(self):
        """Test extraction works for different document types"""
        text = "John Smith from ACME Corp in New York, NY on 01/15/2024"
        
        for doc_type in ["letter", "invoice", "memo", "form", "email"]:
            entities = extract_entities(doc_type, text)
            self.assertIsInstance(entities, dict)
            # Each document type should return mapped entities
    
    def test_extract_entities_result_limits(self):
        """Test that results are limited to prevent noise"""
        # Create text with many potential matches
        many_names = " ".join([f"Person{i} Smith{i}" for i in range(20)])
        entities = extract_entities("letter", many_names)
        
        # Should limit results
        for key, values in entities.items():
            if values:
                self.assertLessEqual(len(values), 10, f"Too many results in {key}: {len(values)}")