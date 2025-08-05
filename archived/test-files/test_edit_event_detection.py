#!/usr/bin/env python3
"""
Test Edit Event button detection
"""
import sys
sys.path.append('/home/schipp0/ePubs_Main')

def test_edit_event_selectors():
    """Test the Edit Event selector logic"""
    
    # Test XPath selectors
    test_buttons = [
        # Should be SELECTED
        ("Edit Event", True),
        ("edit event", True),  # Case insensitive
        ("Edit Event Page", True),  # Contains match
        
        # Should be REJECTED
        ("Manage Event", False),
        ("Manage Event Settings", False),
        ("Edit Manage Event", False),  # Contains "Manage"
        ("Event Management", False),
        ("manage", False),
    ]
    
    print("Edit Event Button Detection Test:")
    print("=" * 50)
    
    for button_text, should_match in test_buttons:
        # Test the logic from the scraper
        button_text_lower = button_text.lower()
        
        # This is the logic from the scraper
        matches = ("manage" not in button_text_lower and 
                  ("edit event" in button_text_lower or "edit" in button_text_lower))
        
        status = "✅" if matches == should_match else "❌"
        print(f"{status} '{button_text}' -> {matches} (expected: {should_match})")
        
        if matches != should_match:
            print(f"    ⚠️  MISMATCH!")
    
    print()
    print("XPath Test - Exact Match:")
    print("=" * 30)
    
    # Test exact match XPath logic
    exact_match_buttons = [
        ("Edit Event", True),
        ("Manage Event", False),
        ("Edit Event Page", False),  # Exact match should fail
        ("edit event", False),  # Case sensitive exact match
    ]
    
    for button_text, should_match in exact_match_buttons:
        matches = (button_text == "Edit Event")
        status = "✅" if matches == should_match else "❌"
        print(f"{status} '{button_text}' -> {matches} (expected: {should_match})")

if __name__ == "__main__":
    test_edit_event_selectors()