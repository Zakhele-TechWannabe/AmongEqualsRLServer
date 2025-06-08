from src.models.world_state import WorldState, WeatherType
from src.utils.action_definitions import ActionType
from traceback import format_exc

def test_world_state_implementation():
    """Test the world state system implementation"""
    
    print("Testing Among Equals - World State System")
    print("=" * 60)
    
    # Test 1: Basic world creation
    print("\n1. Testing basic world creation:")
    try:
        world = WorldState()
        print(f"✓ Created world: Day {world.current_day}, Population {world.population}")
        print(f"   Food stores: {world.settlement.food_stores}")
        print(f"   Weather: {world.environment.current_weather.value}")
        print(f"   Mood: {world.social_climate.overall_mood:.2f}")
    except Exception as e:
        print(f"✗ Failed to create world: {e}")
        return
    
    # Test 2: Settlement resource management
    print("\n2. Testing settlement resource management:")
    try:
        world = WorldState()
        
        # Test per capita calculations
        per_capita = world.settlement.get_resource_per_capita(world.population)
        print(f"✓ Per capita resources: {per_capita}")
        
        # Test daily consumption
        consumption = world.settlement.consume_daily_resources(world.population)
        print(f"✓ Daily consumption: food={consumption['food_consumed']:.1f}, spoilage={consumption['spoilage']:.1f}")
        print(f"   Food stores after consumption: {world.settlement.food_stores:.1f}")
        
    except Exception as e:
        print(f"✗ Settlement management failed: {e}")
        return
    
    # Test 3: Governance system
    print("\n3. Testing governance system:")
    try:
        world = WorldState()
        
        # Add a proposal
        world.governance.add_proposal(
            "rule_001", "alice", "rule", 
            "No hoarding food", world.current_day + 2
        )
        
        # Cast some votes
        world.governance.cast_vote("rule_001", "alice", "for")
        world.governance.cast_vote("rule_001", "bob", "for")
        world.governance.cast_vote("rule_001", "charlie", "against")
        
        proposal = world.governance.get_proposal("rule_001")
        print(f"✓ Proposal votes: {proposal['votes_for']} for, {proposal['votes_against']} against")
        
        # Test proposal resolution
        world.current_day += 3
        resolved = world.governance.resolve_proposals(world.current_day, world.population)
        print(f"✓ Resolved {len(resolved)} proposals")
        if resolved:
            print(f"   Proposal passed: {resolved[0]['passed']}")
        
    except Exception as e:
        print(f"✗ Governance system failed: {e}")
        return
    
    # Test 4: Environmental system
    print("\n4. Testing environmental system:")
    try:
        world = WorldState()
        
        # Test weather effects
        world.environment.current_weather = WeatherType.STORM
        world.environment.weather_severity = 0.7
        
        effects = world.environment.get_environmental_effects()
        print(f"✓ Storm effects: gathering={effects['gathering_efficiency']:.2f}, mood={effects['mood_impact']:.2f}")
        
        # Test daily advancement
        initial_weather = world.environment.current_weather
        for _ in range(5):  # Advance 5 days
            world.environment.advance_day()
        
        print(f"✓ Weather progression: {initial_weather.value} → {world.environment.current_weather.value}")
        print(f"   Season: {world.environment.season}, days in season: {world.environment.days_in_season}")
        
    except Exception as e:
        print(f"✗ Environmental system failed: {e}")
        return
    
    # Test 5: Social climate
    print("\n5. Testing social climate:")
    try:
        world = WorldState()
        
        initial_mood = world.social_climate.overall_mood
        
        # Add positive social event
        world.social_climate.add_social_event(
            'cooperation', 0.1, 'Community worked together on shelter', ['alice', 'bob']
        )
        
        positive_mood = world.social_climate.overall_mood
        
        # Add negative social event
        world.social_climate.add_social_event(
            'conflict', -0.15, 'Argument over resource distribution', ['charlie', 'diana']
        )
        
        final_mood = world.social_climate.overall_mood
        
        print(f"✓ Mood changes: {initial_mood:.2f} → {positive_mood:.2f} → {final_mood:.2f}")
        print(f"   Recent events: {len(world.social_climate.recent_events)}")
        print(f"   Cooperation level: {world.social_climate.cooperation_level:.2f}")
        
    except Exception as e:
        print(f"✗ Social climate failed: {e}")
        return
    
    # Test 6: Day advancement
    print("\n6. Testing day advancement:")
    try:
        world = WorldState()
        
        initial_day = world.current_day
        initial_food = world.settlement.food_stores
        
        # Advance several days
        for _ in range(3):
            daily_summary = world.advance_day()
        
        print(f"✓ Advanced from day {initial_day} to day {world.current_day}")
        print(f"   Food: {initial_food:.1f} → {world.settlement.food_stores:.1f}")
        print(f"   Last day summary keys: {list(daily_summary.keys())}")
        
    except Exception as e:
        print(f"✗ Day advancement failed: {e}")
        return
    
    # Test 7: Action processing
    print("\n7. Testing action processing:")
    try:
        world = WorldState()
        
        initial_food = world.settlement.food_stores
        initial_materials = world.settlement.material_stores
        
        # Process successful food gathering
        food_result = world.process_action_outcome(
            "alice", ActionType.GATHER_FOOD, True, {'amount_gathered': 5.0}
        )
        
        # Process shelter building
        shelter_result = world.process_action_outcome(
            "bob", ActionType.BUILD_SHELTER, True, {'materials_used': 5.0}
        )
        
        print(f"✓ Food gathering: {food_result}")
        print(f"   Food: {initial_food:.1f} → {world.settlement.food_stores:.1f}")
        
        print(f"✓ Shelter building: {shelter_result}")
        print(f"   Materials: {initial_materials:.1f} → {world.settlement.material_stores:.1f}")
        print(f"   Shelter capacity: {world.settlement.shelter_capacity}")
        
    except Exception as e:
        print(f"✗ Action processing failed: {e}")
        return
    
    # Test 8: World summary and context
    print("\n8. Testing world summary and context:")
    try:
        world = WorldState()
        world.add_npc("alice")
        world.add_npc("bob")
        
        summary = world.get_world_summary()
        context = world.get_npc_world_context("alice")
        
        print(f"✓ World summary generated:")
        print(f"   Day: {summary['basic_info']['day']}")
        print(f"   Population: {summary['basic_info']['population']}")
        print(f"   Mood: {summary['social']['mood_description']}")
        print(f"   Urgent issues: {summary['urgent_issues']}")
        
        print(f"✓ NPC context generated:")
        print(f"   Settlement mood: {context['settlement_mood']:.2f}")
        print(f"   Has leader: {context['has_leader']}")
        print(f"   Food per capita: {context['settlement_resources']['food']:.2f}")
        
    except Exception as e:
        print(f"✗ World summary/context failed: {e}")
        return
    
    # Test 9: Serialization
    print("\n9. Testing serialization:")
    try:
        # Create complex world state
        original = WorldState()
        original.current_day = 50
        original.add_npc("alice")
        original.add_npc("bob")
        original.governance.current_leader = "alice"
        original.governance.add_proposal("test", "bob", "rule", "Test rule", 52)
        original.social_climate.add_social_event('cooperation', 0.05, 'Test event')
        
        # Test dict conversion
        data_dict = original.to_dict()
        from_dict = WorldState.from_dict(data_dict)
        
        # Test JSON conversion
        json_str = original.to_json()
        from_json = WorldState.from_json(json_str)
        
        # Verify they're the same
        checks = [
            original.current_day == from_dict.current_day == from_json.current_day,
            original.population == from_dict.population == from_json.population,
            original.governance.current_leader == from_dict.governance.current_leader,
            len(original.governance.active_proposals) == len(from_dict.governance.active_proposals)
        ]
        
        if all(checks):
            print("✓ Serialization working correctly")
        else:
            print("✗ Serialization failed - data doesn't match")
    except Exception as e:
        print(format_exc())
        print(f"✗ Serialization failed: {e}")
    
    # Test 10: Integration stress test
    print("\n10. Testing integration stress test:")
    try:
        world = WorldState()
        
        # Add NPCs
        for i in range(5):
            world.add_npc(f"npc_{i}")
        
        # Simulate complex scenario
        for day in range(10):
            # Process various actions
            world.process_action_outcome(f"npc_{day % 5}", ActionType.GATHER_FOOD, True)
            world.process_action_outcome(f"npc_{(day + 1) % 5}", ActionType.HELP_RANDOM_NPC, True)
            
            # Add governance activity
            if day == 3:
                world.governance.add_proposal(f"prop_{day}", f"npc_{day % 5}", "rule", "Test rule", day + 3)
            
            # Advance day
            daily_summary = world.advance_day()
        
        final_summary = world.get_world_summary()
        
        print(f"✓ Stress test completed:")
        print(f"   Final day: {world.current_day}")
        print(f"   Population: {world.population}")
        print(f"   Food stores: {world.settlement.food_stores:.1f}")
        print(f"   Mood: {final_summary['social']['mood_description']}")
        print(f"   Proposals resolved: {len(world.governance.established_rules)}")
        
    except Exception as e:
        print(f"✗ Integration stress test failed: {e}")
    
    print("\n" + "=" * 60)
    print("World State system test completed!")
    print("If all tests show ✓, your world is ready for NPCs to inhabit!")


if __name__ == "__main__":
    test_world_state_implementation()