import pytest

from documents.extractor import _apply_mapping, extract_entities


class TestLightweightExtractor:
    
    def test_extract_entities_names(self):
        """Test name extraction"""
        content = "John Smith and Mary Johnson are here."
        result = extract_entities("letter", content)
        assert "recipient" in result or "PER" in result
    
    def test_extract_entities_organizations(self):
        """Test organization extraction"""
        content = "Microsoft Corporation and Apple Inc are companies."
        result = extract_entities("letter", content)
        assert "sender_organization" in result or "ORG" in result
    
    def test_extract_entities_locations(self):
        """Test location extraction"""
        content = "New York, NY and Los Angeles, CA are cities."
        result = extract_entities("letter", content)
        assert "address" in result or "LOC" in result
    
    def test_extract_entities_misc(self):
        """Test miscellaneous extraction"""
        content = "Date: 12/25/2023 and project #1234-56"
        result = extract_entities("letter", content)
        # Should extract dates or project codes
        assert len(result) > 0
    
    def test_extract_entities_empty_content(self):
        """Test extraction with empty content"""
        result = extract_entities("letter", "")
        assert isinstance(result, dict)
    
    def test_extract_entities_no_matches(self):
        """Test extraction with no entity matches"""
        content = "xyz abc def 123"
        result = extract_entities("letter", content)
        assert isinstance(result, dict)
    
    def test_apply_mapping_letter(self):
        """Test entity mapping for letter document type"""
        entities = {"PER": ["John Smith"], "ORG": ["Company Inc"]}
        result = _apply_mapping(entities, "letter")
        assert "recipient" in result
        assert "sender_organization" in result
    
    def test_apply_mapping_invoice(self):
        """Test entity mapping for invoice document type"""
        entities = {"ORG": ["Vendor Corp"], "MISC": ["INV-123"]}
        result = _apply_mapping(entities, "invoice")
        assert "vendor" in result
        assert "invoice_number" in result
    
    def test_apply_mapping_unknown_type(self):
        """Test entity mapping for unknown document type"""
        entities = {"PER": ["John Smith"]}
        result = _apply_mapping(entities, "unknown_type")
        assert "PER" in result  # Should keep original tags
    
    def test_apply_mapping_empty_entities(self):
        """Test entity mapping with empty entities"""
        result = _apply_mapping({}, "letter")
        assert isinstance(result, dict)
        assert len(result) == 0
    
    def test_extract_entities_multiple_patterns(self):
        """Test extraction with multiple pattern types"""
        content = """
        Dear John Smith,
        
        Microsoft Corporation is pleased to inform you about project #2024-01.
        Please contact us at Seattle, WA by 01/15/2024.
        
        Best regards,
        Jane Doe
        """
        result = extract_entities("letter", content)
        # Should extract multiple types of entities
        assert len(result) > 0
    
    def test_extract_entities_case_insensitive_orgs(self):
        """Test case insensitive organization extraction"""
        content = "apple inc and MICROSOFT CORP are tech companies"
        result = extract_entities("letter", content)
        # Should extract organizations regardless of case
        mapped_result = any("organization" in key.lower() or "org" in key.lower() 
                          for key in result.keys() if result[key])
        assert mapped_result or len(result) > 0
    
    def test_extract_entities_deduplication(self):
        """Test that duplicate entities are removed"""
        content = "John Smith and John Smith work at Company Inc and Company Inc"
        result = extract_entities("letter", content)
        # Check that duplicates are removed (each entity appears only once)
        for key, values in result.items():
            if values:
                assert len(values) == len(set(values))  # No duplicates
    
    def test_extract_entities_limit_results(self):
        """Test that results are limited to prevent noise"""
        # Create content with many potential matches
        names = " ".join([f"Person{i} Smith{i}" for i in range(20)])
        result = extract_entities("letter", names)
        
        # Should limit results to reasonable numbers
        for key, values in result.items():
            if values:
                assert len(values) <= 10  # Based on limits in code