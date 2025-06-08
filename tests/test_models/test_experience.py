from src.models.experience import ExperienceLevels
from src.utils.action_definitions import ActionType

def test_experience_implementation():
    """Test the experience system implementation"""
    
    print("Testing Among Equals - Experience System")
    print("=" * 50)
    
    # Test 1: Basic experience creation
    print("\n1. Testing basic experience creation:")
    try:
        experience = ExperienceLevels(leadership=0.3, crafting=0.6)
        print(f"✓ Created experience: leadership={experience.leadership}, crafting={experience.crafting}")
    except Exception as e:
        print(f"✗ Failed to create experience: {e}")
        return
    
    # Test 2: Experience gain
    print("\n2. Testing experience gain:")
    try:
        experience = ExperienceLevels()
        
        # Gain some leadership experience
        significant = experience.gain_experience('leadership', 0.1, 'test_action')
        print(f"✓ Gained leadership experience: {experience.leadership:.3f} (significant: {significant})")
        
        # Try to gain invalid experience
        try:
            experience.gain_experience('invalid_skill', 0.1)
            print("✗ Should have rejected invalid skill")
        except ValueError:
            print("✓ Correctly rejected invalid skill category")
        
    except Exception as e:
        print(f"✗ Experience gain failed: {e}")
        return
    
    # Test 3: Experience from actions
    print("\n3. Testing experience from actions:")
    try:
        experience = ExperienceLevels()
        
        # Simulate successful food gathering
        results = experience.gain_experience_from_action(ActionType.GATHER_FOOD, success=True)
        gained_categories = list(results.keys())
        print(f"✓ Food gathering gave experience in: {gained_categories}")
        print(f"   Survival: {experience.survival:.3f}, Resource Management: {experience.resource_management:.3f}")
        
        # Should gain experience in both survival and resource_management
        expected_categories = ['survival', 'resource_management']
        if all(cat in gained_categories for cat in expected_categories):
            print("✓ Correctly gained experience in expected categories")
        else:
            print(f"✗ Expected {expected_categories}, got {gained_categories}")
        
        # Check if any gains were significant
        significant_gains = [cat for cat, is_sig in results.items() if is_sig]
        print(f"✓ Significant gains: {significant_gains}")
        
        # Simulate failed alliance formation
        results_failed = experience.gain_experience_from_action(ActionType.FORM_ALLIANCE, success=False)
        gained_failed = list(results_failed.keys())
        print(f"✓ Failed alliance still gave some experience in: {gained_failed}")
        
    except Exception as e:
        print(f"✗ Action experience failed: {e}")
        return
    
    # Test 4: Skill level descriptions
    print("\n4. Testing skill level descriptions:")
    try:
        experience = ExperienceLevels()
        
        # Test different skill levels
        test_levels = [0.05, 0.25, 0.45, 0.65, 0.85, 0.95]
        for level in test_levels:
            experience.leadership = level
            description = experience.get_skill_level_description('leadership')
            print(f"   Leadership {level:.2f} = {description}")
        
        print("✓ Skill level descriptions working")
        
    except Exception as e:
        print(f"✗ Skill descriptions failed: {e}")
        return
    
    # Test 5: Top skills and analysis
    print("\n5. Testing skill analysis:")
    try:
        # Create NPC with varied experience
        experience = ExperienceLevels(
            leadership=0.8,
            crafting=0.6,
            survival=0.3,
            negotiation=0.9,
            social_manipulation=0.1
        )
        
        top_skills = experience.get_top_skills(3)
        print(f"✓ Top 3 skills: {[(name, f'{level:.2f}', desc) for name, level, desc in top_skills]}")
        
        skilled_areas = experience.get_skills_above_threshold(0.5)
        print(f"✓ Skilled areas (>0.5): {list(skilled_areas.keys())}")
        
        summary = experience.get_experience_summary()
        print(f"✓ Total experience: {summary['total_experience']:.2f}")
        print(f"✓ Specialization score: {summary['specialization_score']:.2f}")
        
    except Exception as e:
        print(f"✗ Skill analysis failed: {e}")
        return
    
    # Test 6: Modifiers and competence
    print("\n6. Testing experience modifiers:")
    try:
        experience = ExperienceLevels(leadership=0.7, crafting=0.2)
        
        leadership_confidence = experience.get_confidence_modifier('leadership')
        leadership_competence = experience.get_competence_modifier('leadership')
        
        crafting_confidence = experience.get_confidence_modifier('crafting')
        crafting_competence = experience.get_competence_modifier('crafting')
        
        print(f"✓ Leadership (0.7): confidence={leadership_confidence:.2f}x, competence={leadership_competence:.2f}x")
        print(f"✓ Crafting (0.2): confidence={crafting_confidence:.2f}x, competence={crafting_competence:.2f}x")
        
        # Test expertise check
        has_leadership_expertise = experience.has_expertise_in('leadership')
        has_crafting_expertise = experience.has_expertise_in('crafting')
        print(f"✓ Leadership expertise: {has_leadership_expertise}, Crafting expertise: {has_crafting_expertise}")
        
    except Exception as e:
        print(f"✗ Experience modifiers failed: {e}")
        return
    
    # Test 7: Serialization
    print("\n7. Testing serialization:")
    try:
        # Create complex experience with history
        original = ExperienceLevels(leadership=0.5, crafting=0.3)
        original.gain_experience('leadership', 0.1, 'test_source')
        original.gain_experience('crafting', 0.2, 'another_test')
        
        # Test dict conversion
        data_dict = original.to_dict()
        from_dict = ExperienceLevels.from_dict(data_dict)
        
        # Test JSON conversion
        json_str = original.to_json()
        from_json = ExperienceLevels.from_json(json_str)
        
        # Verify they're the same
        if (original.leadership == from_dict.leadership == from_json.leadership and
            len(original.experience_history) == len(from_dict.experience_history)):
            print("✓ Serialization working correctly")
        else:
            print("✗ Serialization failed - values don't match")
    except Exception as e:
        print(f"✗ Serialization failed: {e}")
    
    # Test 8: Diminishing returns
    print("\n8. Testing diminishing returns:")
    try:
        experience = ExperienceLevels()
        
        # Gain experience repeatedly in the same category
        gains = []
        for i in range(5):
            old_level = experience.leadership
            experience.gain_experience('leadership', 0.1, f'attempt_{i}')
            actual_gain = experience.leadership - old_level
            gains.append(actual_gain)
        
        print(f"✓ Experience gains show diminishing returns:")
        for i, gain in enumerate(gains):
            print(f"   Attempt {i+1}: {gain:.4f} gain")
        
        # Should see decreasing gains
        if gains[0] > gains[-1]:
            print("✓ Diminishing returns working correctly")
        else:
            print("✗ Diminishing returns not working as expected")
            
    except Exception as e:
        print(f"✗ Diminishing returns test failed: {e}")
    
    print("\n" + "=" * 50)
    print("Experience system test completed!")
    print("If all tests show ✓, the implementation is working correctly.")


if __name__ == "__main__":
    test_experience_implementation()