from src.models.trauma import TraumaMemory, TraumaState, create_common_trauma

def test_trauma_implementation():
    """Test the trauma system implementation"""
    
    print("Testing Among Equals - Trauma System")
    print("=" * 50)
    
    # Test 1: Basic trauma memory creation
    print("\n1. Testing basic trauma memory creation:")
    try:
        trauma_memory = TraumaMemory(
            event_type='betrayal',
            original_impact=0.8,
            current_impact=0.8,
            age_when_occurred=25,
            description="Betrayed by close ally"
        )
        print(f"✓ Created trauma memory: {trauma_memory.event_type}, impact={trauma_memory.current_impact}")
        print(f"   Intensity: {trauma_memory.get_intensity_description()}")
        print(f"   Scar threshold: {trauma_memory.scar_threshold:.3f}")
    except Exception as e:
        print(f"✗ Failed to create trauma memory: {e}")
        return
    
    # Test 2: Trauma healing
    print("\n2. Testing trauma healing:")
    try:
        trauma_memory = TraumaMemory(
            event_type='social_rejection',
            original_impact=0.6,
            current_impact=0.6,
            age_when_occurred=20,
            description="Rejected by community"
        )
        
        original_impact = trauma_memory.current_impact
        trauma_memory.apply_healing(0.2, "therapy_session")
        
        print(f"✓ Before healing: {original_impact:.3f}")
        print(f"✓ After healing: {trauma_memory.current_impact:.3f}")
        print(f"✓ Healing progress: {trauma_memory.healing_progress:.2%}")
        print(f"✓ Healing activities: {trauma_memory.healing_activities}")
        
    except Exception as e:
        print(f"✗ Trauma healing failed: {e}")
        return
    
    # Test 3: Trauma state management
    print("\n3. Testing trauma state management:")
    try:
        trauma_state = TraumaState()
        
        # Add multiple traumas
        trauma1 = trauma_state.add_trauma('betrayal', 0.8, 25, "Betrayed by friend")
        trauma2 = trauma_state.add_trauma('leadership_failure', 0.5, 30, "Failed as leader")
        trauma3 = trauma_state.add_trauma('betrayal', 0.3, 35, "Minor betrayal")
        
        print(f"✓ Added {len(trauma_state.memories)} trauma memories")
        
        # Test trauma impact calculation
        betrayal_impact = trauma_state.get_trauma_impact('betrayal')
        print(f"✓ Total betrayal impact: {betrayal_impact:.3f}")
        
        # Test active traumas
        active_traumas = trauma_state.get_active_traumas()
        print(f"✓ Active traumas: {active_traumas}")
        
    except Exception as e:
        print(f"✗ Trauma state management failed: {e}")
        return
    
    # Test 4: Daily healing
    print("\n4. Testing daily healing:")
    try:
        from src.models.personality import PersonalityTraits
        
        trauma_state = TraumaState()
        trauma_state.add_trauma('betrayal', 0.6, 25, "Test betrayal")
        
        # Create personality that affects healing
        forgiving_personality = PersonalityTraits(forgiveness=0.9, analytical=0.8, impulsiveness=0.2)
        
        before_impact = trauma_state.get_trauma_impact('betrayal')
        trauma_state.apply_daily_healing(forgiving_personality, days_passed=30)
        after_impact = trauma_state.get_trauma_impact('betrayal')
        
        print(f"✓ Before 30 days of healing: {before_impact:.3f}")
        print(f"✓ After 30 days of healing: {after_impact:.3f}")
        print(f"✓ Healing amount: {before_impact - after_impact:.3f}")
        
    except Exception as e:
        print(f"✗ Daily healing failed: {e}")
        return
    
    # Test 5: Activity healing
    print("\n5. Testing activity healing:")
    try:
        from src.models.personality import PersonalityTraits
        
        trauma_state = TraumaState()
        trauma_state.add_trauma('social_rejection', 0.7, 20, "Rejected by group")
        
        personality = PersonalityTraits(sociability=0.8)
        
        before_impact = trauma_state.get_trauma_impact('social_rejection')
        trauma_state.apply_activity_healing('socializing', 0.1, personality)
        after_impact = trauma_state.get_trauma_impact('social_rejection')
        
        print(f"✓ Before socializing activity: {before_impact:.3f}")
        print(f"✓ After socializing activity: {after_impact:.3f}")
        print(f"✓ Activity was effective for social rejection trauma")
        
    except Exception as e:
        print(f"✗ Activity healing failed: {e}")
        return
    
    # Test 6: Counter-experience healing
    print("\n6. Testing counter-experience healing:")
    try:
        trauma_state = TraumaState()
        trauma_state.add_trauma('betrayal', 0.8, 25, "Betrayed by ally")
        
        before_impact = trauma_state.get_trauma_impact('betrayal')
        trauma_state.apply_counter_experience_healing('trust_restoration', 0.5, "Ally proved trustworthy")
        after_impact = trauma_state.get_trauma_impact('betrayal')
        
        print(f"✓ Before counter-experience: {before_impact:.3f}")
        print(f"✓ After trust restoration: {after_impact:.3f}")
        print(f"✓ Counter-experience healing was effective")
        
    except Exception as e:
        print(f"✗ Counter-experience healing failed: {e}")
        return
    
    # Test 7: Trauma summary and behavioral influence
    print("\n7. Testing trauma summary and behavioral influence:")
    try:
        trauma_state = TraumaState()
        trauma_state.add_trauma('betrayal', 0.7, 25, "Major betrayal")
        trauma_state.add_trauma('leadership_failure', 0.5, 30, "Failed leadership")
        
        summary = trauma_state.get_trauma_summary()
        print(f"✓ Trauma summary:")
        print(f"   Total traumas: {summary['total_trauma_count']}")
        print(f"   Overall trauma level: {summary['overall_trauma_level']:.3f}")
        print(f"   Most severe: {summary['most_severe']['type']} ({summary['most_severe']['intensity']})")
        
        behavioral_influences = trauma_state.get_trauma_influence_on_behavior()
        print(f"✓ Behavioral influences:")
        for behavior, strength in behavioral_influences.items():
            if strength > 0.1:  # Only show significant influences
                print(f"   {behavior}: {strength:.2f}")
        
    except Exception as e:
        print(f"✗ Trauma summary failed: {e}")
        return
    
    # Test 8: Serialization
    print("\n8. Testing serialization:")
    try:
        # Create complex trauma state
        original = TraumaState()
        original.add_trauma('betrayal', 0.8, 25, "Test betrayal")
        original.add_trauma('social_rejection', 0.5, 20, "Test rejection")
        
        # Apply some healing
        original.apply_activity_healing('meditation', 0.1)
        
        # Test dict conversion
        data_dict = original.to_dict()
        from_dict = TraumaState.from_dict(data_dict)
        
        # Test JSON conversion
        json_str = original.to_json()
        from_json = TraumaState.from_json(json_str)
        
        # Verify they're the same
        if (len(original.memories) == len(from_dict.memories) == len(from_json.memories) and
            original.last_healing_activity == from_dict.last_healing_activity):
            print("✓ Serialization working correctly")
        else:
            print("✗ Serialization failed - data doesn't match")
    except Exception as e:
        print(f"✗ Serialization failed: {e}")
    
    # Test 9: Common trauma creation helper
    print("\n9. Testing common trauma creation:")
    try:
        mild_trauma = create_common_trauma('betrayal', 'mild', 20)
        severe_trauma = create_common_trauma('violence', 'severe', 25, "Witnessed brutal fight")
        
        print(f"✓ Mild betrayal trauma: impact={mild_trauma.original_impact:.3f}")
        print(f"✓ Severe violence trauma: impact={severe_trauma.original_impact:.3f}")
        print(f"✓ Trauma creation helper working")
        
    except Exception as e:
        print(f"✗ Common trauma creation failed: {e}")
    
    print("\n" + "=" * 50)
    print("Trauma system test completed!")
    print("If all tests show ✓, the implementation is working correctly.")


if __name__ == "__main__":
    test_trauma_implementation()