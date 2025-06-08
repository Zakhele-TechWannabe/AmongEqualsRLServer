from src.models.npc import NPCState, PersonalityTraits
from src.utils.action_definitions import ActionType

def test_npc_implementation():
    """Test the complete NPC implementation"""
    
    print("Testing Among Equals - Complete NPC System")
    print("=" * 60)
    
    # Test 1: Basic NPC creation
    print("\n1. Testing basic NPC creation:")
    try:
        npc = NPCState(
            npc_id="test_001",
            name="Alice",
            age=25,
            health=0.8,
            personality=PersonalityTraits.from_archetype('social_leader')
        )
        print(f"✓ Created NPC: {npc.name} (ID: {npc.npc_id}, Age: {npc.age})")
        print(f"   Physical condition: {npc.get_physical_condition()}")
        print(f"   Personality: {npc.personality.get_personality_summary()}")
    except Exception as e:
        print(f"✗ Failed to create NPC: {e}")
        return
    
    # Test 2: Random NPC generation
    print("\n2. Testing random NPC generation:")
    try:
        random_npc = NPCState.create_random_npc("random_001", "Bob")
        print(f"✓ Generated random NPC: {random_npc.name}")
        print(f"   Age: {random_npc.age}, Health: {random_npc.health:.2f}")
        print(f"   Personality: {random_npc.personality.get_personality_summary()}")
        print(f"   Top skills: {[f'{name}({level:.2f})' for name, level, _ in random_npc.experience.get_top_skills()]}")
        
        if random_npc.trauma.memories:
            print(f"   Trauma count: {len(random_npc.trauma.memories)}")
        else:
            print(f"   No trauma")
    except Exception as e:
        print(f"✗ Random NPC generation failed: {e}")
        return
    
    # Test 3: Archetype NPC creation
    print("\n3. Testing archetype NPC creation:")
    try:
        archetypes = ['social_leader', 'greedy_loner', 'analytical_planner', 'traumatized_survivor']
        
        for archetype in archetypes:
            npc = NPCState.create_npc_with_archetype(f"{archetype}_001", archetype, age=30)
            trauma_count = len(npc.trauma.memories)
            top_skill = npc.experience.get_top_skills(1)[0] if npc.experience.get_top_skills(1) else ("none", 0, "")
            
            print(f"✓ {archetype}: trauma={trauma_count}, top_skill={top_skill[0]}({top_skill[1]:.2f})")
    except Exception as e:
        print(f"✗ Archetype NPC creation failed: {e}")
        return
    
    # Test 4: Action processing
    print("\n4. Testing action processing:")
    try:
        npc = NPCState.create_random_npc("action_test", "Charlie")
        
        initial_hunger = npc.hunger_level
        initial_energy = npc.energy_level
        
        # Test successful food gathering
        outcome = npc.perform_action(
            ActionType.GATHER_FOOD, 
            success=True, 
            outcome_data={'food_gained': 0.2}
        )
        
        print(f"✓ Food gathering results: {list(outcome.keys())}")
        print(f"   Hunger: {initial_hunger:.2f} → {npc.hunger_level:.2f}")
        print(f"   Energy: {initial_energy:.2f} → {npc.energy_level:.2f}")
        print(f"   Last action: {npc.last_action} (success: {npc.last_action_success})")
        
    except Exception as e:
        print(f"✗ Action processing failed: {e}")
        return
    
    # Test 5: Social interactions
    print("\n5. Testing social interactions:")
    try:
        npc1 = NPCState.create_random_npc("social_001", "David")
        target_npc = "eve_002"
        
        # Test positive interaction
        result = npc1.interact_with_npc(target_npc, 'help_request', 'success')
        relationship = npc1.relationships.get_relationship(target_npc)
        
        print(f"✓ Help request result: {result['outcome']}")
        print(f"   New relationship type: {result['new_relationship_type']}")
        print(f"   Trust level: {relationship.trust:.3f}")
        print(f"   Affection level: {relationship.affection:.3f}")
        
        # Test traumatic interaction
        betrayal_result = npc1.interact_with_npc(target_npc, 'betrayal', 'success')
        trauma_count = len(npc1.trauma.memories)
        
        print(f"✓ Betrayal processed, trauma memories: {trauma_count}")
        
    except Exception as e:
        print(f"✗ Social interactions failed: {e}")
        return
    
    # Test 6: Daily life simulation
    print("\n6. Testing daily life simulation:")
    try:
        npc = NPCState.create_npc_with_archetype("daily_001", "traumatized_survivor", age=25)
        
        initial_trauma_impact = npc.trauma.get_trauma_impact('violence') if npc.trauma.get_active_traumas() else 0
        initial_age = npc.age
        
        # Simulate 30 days with healing activities
        for day in range(30):
            activities = ['meditation', 'socializing'] if day % 3 == 0 else []
            npc.advance_day(activities)
        
        final_trauma_impact = npc.trauma.get_trauma_impact('violence') if npc.trauma.get_active_traumas() else 0
        
        print(f"✓ Simulated 30 days:")
        print(f"   Days alive: {npc.days_alive}")
        print(f"   Age: {initial_age} → {npc.age}")
        print(f"   Trauma healing: {initial_trauma_impact:.3f} → {final_trauma_impact:.3f}")
        print(f"   Physical condition: {npc.get_physical_condition()}")
        
    except Exception as e:
        print(f"✗ Daily life simulation failed: {e}")
        return
    
    # Test 7: Character analysis
    print("\n7. Testing character analysis:")
    try:
        npc = NPCState.create_npc_with_archetype("analysis_001", "social_leader", age=35)
        
        # Add some relationships and interactions
        npc.interact_with_npc('friend1', 'help_request', 'success')
        npc.interact_with_npc('enemy1', 'conflict', 'failure')
        npc.perform_action(ActionType.FORM_ALLIANCE, True, {'target_npc': 'ally1'})
        
        summary = npc.get_character_summary()
        decision_context = npc.get_decision_context()
        
        print(f"✓ Character summary generated:")
        print(f"   Name: {summary['basic_info']['name']}")
        print(f"   Personality: {summary['personality']['summary']}")
        print(f"   Top skill: {summary['experience']['top_skills'][0][0] if summary['experience']['top_skills'] else 'none'}")
        print(f"   Social isolation: {summary['relationships']['social_isolation']:.3f}")
        print(f"   Trauma count: {summary['trauma']['trauma_count']}")
        
        print(f"✓ Decision context prepared (keys: {list(decision_context.keys())})")
        
    except Exception as e:
        print(f"✗ Character analysis failed: {e}")
        return
    
    # Test 8: Physical state management
    print("\n8. Testing physical state management:")
    try:
        npc = NPCState(npc_id="physical_001", health=0.2, hunger_level=0.9, energy_level=0.1)
        
        urgent_needs = npc.needs_immediate_attention()
        condition = npc.get_physical_condition()
        
        print(f"✓ Physical state assessment:")
        print(f"   Condition: {condition}")
        print(f"   Urgent needs: {urgent_needs}")
        
        # Test physical updates
        npc.update_physical_state(health_change=0.3, hunger_change=-0.4, energy_change=0.6)
        
        new_condition = npc.get_physical_condition()
        new_needs = npc.needs_immediate_attention()
        
        print(f"   After treatment: {new_condition}")
        print(f"   Remaining needs: {new_needs}")
        
    except Exception as e:
        print(f"✗ Physical state management failed: {e}")
        return
    
    # Test 9: Serialization
    print("\n9. Testing serialization:")
    try:
        # Create complex NPC
        original = NPCState.create_npc_with_archetype("serialize_001", "social_leader", "TestNPC", 30)
        original.interact_with_npc('friend1', 'help_request', 'success')
        original.perform_action(ActionType.GATHER_FOOD, True)
        original.advance_day(['meditation'])
        
        # Test dict conversion
        data_dict = original.to_dict()
        from_dict = NPCState.from_dict(data_dict)
        
        # Test JSON conversion
        json_str = original.to_json()
        from_json = NPCState.from_json(json_str)
        
        # Verify they're the same
        checks = [
            original.npc_id == from_dict.npc_id == from_json.npc_id,
            original.name == from_dict.name == from_json.name,
            len(original.relationships.relationships) == len(from_dict.relationships.relationships),
            original.last_action == from_dict.last_action == from_json.last_action
        ]
        
        if all(checks):
            print("✓ Serialization working correctly")
        else:
            print("✗ Serialization failed - data doesn't match")
    except Exception as e:
        print(f"✗ Serialization failed: {e}")
    
    # Test 10: Integration validation
    print("\n10. Testing system integration:")
    try:
        npc = NPCState.create_random_npc("integration_001", "Integration_Test")
        
        # Verify all systems are properly integrated
        systems_check = {
            'personality': hasattr(npc.personality, 'greed'),
            'experience': hasattr(npc.experience, 'leadership'),
            'trauma': hasattr(npc.trauma, 'memories'),
            'relationships': hasattr(npc.relationships, 'relationships'),
            'decision_context': 'personality_traits' in npc.get_decision_context(),
            'character_summary': 'basic_info' in npc.get_character_summary()
        }
        
        all_systems_working = all(systems_check.values())
        
        print(f"✓ System integration check:")
        for system, working in systems_check.items():
            status = "✓" if working else "✗"
            print(f"   {status} {system}")
        
        if all_systems_working:
            print("✓ All systems fully integrated!")
        else:
            print("✗ Some systems not properly integrated")
            
    except Exception as e:
        print(f"✗ Integration validation failed: {e}")
    
    print("\n" + "=" * 60)
    print("Complete NPC system test completed!")
    print("If all tests show ✓, your NPCs are ready for the modifier pipeline!")


if __name__ == "__main__":
    test_npc_implementation()