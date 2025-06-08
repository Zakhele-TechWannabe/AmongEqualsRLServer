from src.models.personality import PersonalityTraits

def test_personality_implementation():
    """Test the personality system implementation"""
    
    print("Testing Among Equals - Personality System")
    print("=" * 50)
    
    # Test 1: Basic personality creation
    print("\n1. Testing basic personality creation:")
    try:
        personality = PersonalityTraits(greed=0.8, sociability=0.3)
        print(f"✓ Created personality: greed={personality.greed}, sociability={personality.sociability}")
    except Exception as e:
        print(f"✗ Failed to create personality: {e}")
        return
    
    # Test 2: Random personality generation
    print("\n2. Testing random personality generation:")
    try:
        random_personality = PersonalityTraits.generate_random()
        print(f"✓ Generated random personality:")
        for trait, value in random_personality.to_dict().items():
            print(f"   {trait}: {value:.3f}")
    except Exception as e:
        print(f"✗ Failed to generate random personality: {e}")
        return
    
    # Test 3: Archetype personalities
    print("\n3. Testing archetype personalities:")
    archetypes = ['greedy_loner', 'social_leader', 'lazy_follower', 'analytical_planner']
    
    for archetype in archetypes:
        try:
            personality = PersonalityTraits.from_archetype(archetype)
            summary = personality.get_personality_summary()
            print(f"✓ {archetype}: {summary}")
        except Exception as e:
            print(f"✗ Failed to create {archetype}: {e}")
    
    # Test 4: Validation
    print("\n4. Testing validation:")
    try:
        # This should fail
        PersonalityTraits(greed=1.5)
        print("✗ Validation failed - should have rejected greed=1.5")
    except ValueError:
        print("✓ Validation working - correctly rejected invalid value")
    except Exception as e:
        print(f"✗ Unexpected error in validation: {e}")
    
    # Test 5: Serialization
    print("\n5. Testing serialization:")
    try:
        original = PersonalityTraits.from_archetype('social_leader')
        
        # Test dict conversion
        data_dict = original.to_dict()
        from_dict = PersonalityTraits.from_dict(data_dict)
        
        # Test JSON conversion
        json_str = original.to_json()
        from_json = PersonalityTraits.from_json(json_str)
        
        # Verify they're the same
        if (original.greed == from_dict.greed == from_json.greed and
            original.sociability == from_dict.sociability == from_json.sociability):
            print("✓ Serialization working correctly")
        else:
            print("✗ Serialization failed - values don't match")
    except Exception as e:
        print(f"✗ Serialization failed: {e}")
    
    # Test 6: Trait analysis
    print("\n6. Testing trait analysis:")
    try:
        personality = PersonalityTraits.from_archetype('greedy_loner')
        dominant = personality.get_dominant_traits()
        weak = personality.get_weak_traits()
        
        print(f"✓ Dominant traits: {dominant}")
        print(f"✓ Weak traits: {weak}")
        print(f"✓ Personality summary: {personality.get_personality_summary()}")
    except Exception as e:
        print(f"✗ Trait analysis failed: {e}")
    
    print("\n" + "=" * 50)
    print("Personality system test completed!")
    print("If all tests show ✓, the implementation is working correctly.")

if __name__ == "__main__":
    test_personality_implementation()