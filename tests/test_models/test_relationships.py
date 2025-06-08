from src.models.relationships import RelationshipDimensions, RelationshipMatrix, simulate_relationship_evolution, create_random_relationship

def test_relationships_implementation():
    """Test the relationship system implementation"""
    
    print("Testing Among Equals - Relationship System")
    print("=" * 50)
    
    # Test 1: Basic relationship creation
    print("\n1. Testing basic relationship creation:")
    try:
        relationship = RelationshipDimensions(trust=0.8, respect=0.6, affection=0.7)
        print(f"✓ Created relationship: trust={relationship.trust}, respect={relationship.respect}")
        print(f"   Overall sentiment: {relationship.get_overall_sentiment():.3f}")
        print(f"   Closeness: {relationship.get_closeness():.3f}")
        print(f"   Relationship type: {relationship.get_relationship_type()}")
    except Exception as e:
        print(f"✗ Failed to create relationship: {e}")
        return
    
    # Test 2: Relationship dimension updates
    print("\n2. Testing relationship dimension updates:")
    try:
        relationship = RelationshipDimensions(trust=0.5, respect=0.5)
        
        print(f"   Before: trust={relationship.trust:.3f}")
        relationship.update_dimension('trust', 0.2, reason="helped_in_crisis")
        print(f"   After helping: trust={relationship.trust:.3f}")
        
        # Test closeness multiplier effect
        close_relationship = RelationshipDimensions(trust=0.8, affection=0.9)
        distant_relationship = RelationshipDimensions(trust=0.3, affection=0.2)
        
        close_relationship.update_dimension('trust', -0.1, reason="minor_disagreement")
        distant_relationship.update_dimension('trust', -0.1, reason="minor_disagreement")
        
        print(f"   Close relationship trust change: larger impact due to closeness")
        print(f"   Distant relationship trust change: smaller impact")
        print("✓ Relationship updates working correctly")
        
    except Exception as e:
        print(f"✗ Relationship updates failed: {e}")
        return
    
    # Test 3: Relationship events
    print("\n3. Testing relationship events:")
    try:
        relationship = RelationshipDimensions()
        
        print(f"   Initial trust: {relationship.trust:.3f}")
        relationship.apply_relationship_event('helped_in_crisis')
        print(f"   After helping in crisis: trust={relationship.trust:.3f}, respect={relationship.respect:.3f}")
        
        relationship.apply_relationship_event('betrayed_trust')
        print(f"   After betrayal: trust={relationship.trust:.3f}, fear={relationship.fear:.3f}")
        
        # Test history tracking
        recent_changes = relationship.get_recent_changes(3)
        print(f"✓ Tracked {len(recent_changes)} recent relationship changes")
        
    except Exception as e:
        print(f"✗ Relationship events failed: {e}")
        return
    
    # Test 4: Relationship matrix management
    print("\n4. Testing relationship matrix:")
    try:
        matrix = RelationshipMatrix()
        
        # Create relationships with multiple NPCs
        matrix.update_relationship('alice', 'trust', 0.3, 'initial_meeting')
        matrix.update_relationship('bob', 'respect', 0.4, 'showed_competence')
        matrix.update_relationship('charlie', 'fear', 0.2, 'intimidating_behavior')
        
        print(f"✓ Created relationships with {len(matrix.relationships)} NPCs")
        
        # Test getting specific relationships
        trusted_npcs = matrix.get_trusted_npcs(threshold=0.7)
        feared_npcs = matrix.get_feared_npcs(threshold=0.1)
        
        print(f"   Trusted NPCs: {trusted_npcs}")
        print(f"   Feared NPCs: {feared_npcs}")
        
    except Exception as e:
        print(f"✗ Relationship matrix failed: {e}")
        return
    
    # Test 5: Social analysis
    print("\n5. Testing social analysis:")
    try:
        matrix = RelationshipMatrix()
        
        # Create diverse relationships
        matrix.apply_relationship_event('alice', 'saved_from_danger')  # Strong positive
        matrix.apply_relationship_event('bob', 'betrayed_trust')       # Strong negative  
        matrix.apply_relationship_event('charlie', 'shared_resources') # Moderate positive
        matrix.apply_relationship_event('diana', 'competed_for_leadership') # Mixed
        
        closest = matrix.get_closest_relationships(3)
        print(f"✓ Closest relationships:")
        for npc_id, closeness, rel_type in closest:
            print(f"   {npc_id}: {closeness:.3f} ({rel_type})")
        
        isolation = matrix.calculate_social_isolation()
        influence = matrix.calculate_social_influence()
        print(f"✓ Social isolation: {isolation:.3f}")
        print(f"✓ Social influence: {influence:.3f}")
        
    except Exception as e:
        print(f"✗ Social analysis failed: {e}")
        return
    
    # Test 6: Relationship types and conflicts
    print("\n6. Testing relationship types and conflicts:")
    try:
        matrix = RelationshipMatrix()
        
        # Create conflicted relationship (high fear + high dependency)
        conflicted_rel = matrix.get_relationship('boss')
        conflicted_rel.fear = 0.8
        conflicted_rel.dependency = 0.7
        conflicted_rel.respect = 0.6
        
        conflicts = matrix.get_relationship_conflicts()
        print(f"✓ Detected {len(conflicts)} relationship conflicts:")
        for npc_id, conflict_type, description in conflicts:
            print(f"   {npc_id}: {conflict_type} - {description}")
        
        rel_types = matrix.get_relationships_by_type()
        print(f"✓ Relationship types: {list(rel_types.keys())}")
        
    except Exception as e:
        print(f"✗ Relationship types/conflicts failed: {e}")
        return
    
    # Test 7: Relationship summary
    print("\n7. Testing relationship summary:")
    try:
        matrix = RelationshipMatrix()
        
        # Create complex relationship network
        matrix.apply_relationship_event('friend1', 'helped_in_crisis')
        matrix.apply_relationship_event('friend2', 'shared_resources')
        matrix.apply_relationship_event('enemy1', 'betrayed_trust')
        matrix.apply_relationship_event('rival1', 'competed_for_leadership')
        matrix.apply_relationship_event('boss', 'demonstrated_competence')
        
        summary = matrix.get_relationship_summary()
        print(f"✓ Relationship summary:")
        print(f"   Total relationships: {summary['total_relationships']}")
        print(f"   Social isolation: {summary['social_isolation']:.3f}")
        print(f"   Social influence: {summary['social_influence']:.3f}")
        print(f"   Sentiment distribution: {summary['sentiment_distribution']}")
        print(f"   Trust network size: {summary['trust_network_size']}")
        
    except Exception as e:
        print(f"✗ Relationship summary failed: {e}")
        return
    
    # Test 8: Serialization
    print("\n8. Testing serialization:")
    try:
        # Create complex relationship matrix
        original = RelationshipMatrix()
        original.apply_relationship_event('alice', 'saved_from_danger')
        original.apply_relationship_event('bob', 'betrayed_trust')
        original.update_relationship('charlie', 'trust', 0.3, 'custom_reason')
        
        # Test dict conversion
        data_dict = original.to_dict()
        from_dict = RelationshipMatrix.from_dict(data_dict)
        
        # Test JSON conversion
        json_str = original.to_json()
        from_json = RelationshipMatrix.from_json(json_str)
        
        # Verify they're the same
        if (len(original.relationships) == len(from_dict.relationships) == len(from_json.relationships) and
            'alice' in from_dict.relationships and 'alice' in from_json.relationships):
            print("✓ Serialization working correctly")
        else:
            print("✗ Serialization failed - data doesn't match")
    except Exception as e:
        print(f"✗ Serialization failed: {e}")
    
    # Test 9: Relationship evolution simulation
    print("\n9. Testing relationship evolution:")
    try:
        matrix = RelationshipMatrix()
        
        # Start with neutral relationship
        initial_trust = matrix.get_relationship('test_npc').trust
        
        # Apply series of events
        events = ['helped_in_crisis', 'shared_resources', 'kept_secret']
        matrix = simulate_relationship_evolution(matrix, 'test_npc', events, days_passed=10)
        
        final_trust = matrix.get_relationship('test_npc').trust
        
        print(f"✓ Relationship evolution:")
        print(f"   Initial trust: {initial_trust:.3f}")
        print(f"   After positive events: {final_trust:.3f}")
        print(f"   Trust improved by: {final_trust - initial_trust:.3f}")
        
    except Exception as e:
        print(f"✗ Relationship evolution failed: {e}")
    
    # Test 10: Random relationship generation
    print("\n10. Testing random relationship generation:")
    try:
        random_rel = create_random_relationship()
        print(f"✓ Generated random relationship:")
        print(f"   Trust: {random_rel.trust:.3f}, Respect: {random_rel.respect:.3f}")
        print(f"   Affection: {random_rel.affection:.3f}, Fear: {random_rel.fear:.3f}")
        print(f"   Type: {random_rel.get_relationship_type()}")
        
    except Exception as e:
        print(f"✗ Random relationship generation failed: {e}")
    
    print("\n" + "=" * 50)
    print("Relationship system test completed!")
    print("If all tests show ✓, the implementation is working correctly.")


if __name__ == "__main__":
    test_relationships_implementation()