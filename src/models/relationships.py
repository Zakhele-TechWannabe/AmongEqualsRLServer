from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any, Optional
import json
import random
from datetime import datetime


@dataclass
class RelationshipDimensions:
    """Multi-dimensional relationship tracking between two NPCs"""
    
    trust: float = 0.5      # Belief they won't betray/harm you (0.0 - 1.0)
    respect: float = 0.5    # Admiration for their capabilities/character (0.0 - 1.0)
    affection: float = 0.5  # Personal liking/love (0.0 - 1.0)
    dependency: float = 0.0 # How much you need them (0.0 - 1.0)
    fear: float = 0.0      # How much you're afraid of them (0.0 - 1.0)
    
    # Track relationship changes for analysis
    relationship_history: List[Dict[str, Any]] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate relationship values"""
        dimensions = ['trust', 'respect', 'affection', 'dependency', 'fear']
        for dim_name in dimensions:
            value = getattr(self, dim_name)
            if not isinstance(value, (int, float)):
                raise ValueError(f"{dim_name} must be a number, got {type(value)}")
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{dim_name} must be between 0.0 and 1.0, got {value}")
    
    def get_overall_sentiment(self) -> float:
        """Calculate overall positive/negative feeling (-1.0 to 1.0)"""
        positive = (self.trust + self.respect + self.affection) / 3.0
        negative = self.fear
        
        # Convert to -1.0 to 1.0 scale
        sentiment = (positive * 2 - 1.0) - negative
        return max(-1.0, min(1.0, sentiment))
    
    def get_closeness(self) -> float:
        """Calculate emotional closeness (0.0 to 1.0)"""
        # Closeness combines affection, trust, and dependency
        base_closeness = (self.affection + self.trust + self.dependency) / 3.0
        
        # Fear reduces closeness
        fear_penalty = self.fear * 0.5
        
        return max(0.0, base_closeness - fear_penalty)
    
    def get_influence_potential(self) -> float:
        """Calculate how much this NPC could influence decisions (0.0 to 1.0)"""
        # Influence comes from respect, trust, or fear
        positive_influence = (self.respect + self.trust) / 2.0
        fear_influence = self.fear * 0.8  # Fear is somewhat less reliable for influence
        
        return max(positive_influence, fear_influence)
    
    def get_relationship_type(self) -> str:
        """Get a human-readable relationship type"""
        sentiment = self.get_overall_sentiment()
        closeness = self.get_closeness()
        
        if self.fear > 0.7:
            return "feared enemy" if sentiment < -0.3 else "feared authority"
        elif sentiment > 0.6 and closeness > 0.7:
            return "close friend" if self.affection > 0.8 else "trusted ally"
        elif sentiment > 0.3 and closeness > 0.5:
            return "friend"
        elif sentiment > 0.0:
            return "acquaintance"
        elif sentiment > -0.3:
            return "neutral"
        elif sentiment > -0.6:
            return "disliked"
        else:
            return "enemy"
    
    def update_dimension(self, dimension: str, change: float, 
                        reason: str = "unknown", closeness_multiplier: bool = True):
        """Update a relationship dimension with impact scaling"""
        if not hasattr(self, dimension):
            available = ['trust', 'respect', 'affection', 'dependency', 'fear']
            raise ValueError(f"Unknown relationship dimension: {dimension}. Available: {available}")
        
        if not isinstance(change, (int, float)):
            raise ValueError(f"Change must be a number, got {type(change)}")
        
        current_value = getattr(self, dimension)
        
        # Closeness affects impact - closer relationships have bigger emotional swings
        if closeness_multiplier:
            closeness = self.get_closeness()
            impact_multiplier = 1.0 + closeness  # 1.0 to 2.0 multiplier
            adjusted_change = change * impact_multiplier
        else:
            adjusted_change = change
        
        new_value = max(0.0, min(1.0, current_value + adjusted_change))
        old_value = current_value
        setattr(self, dimension, new_value)
        
        # Record the change for analysis
        self.relationship_history.append({
            'dimension': dimension,
            'old_value': old_value,
            'new_value': new_value,
            'change': adjusted_change,
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        })
    
    def apply_relationship_event(self, event_type: str, impact_strength: float = 1.0):
        """Apply predefined relationship events"""
        relationship_events = {
            'helped_in_crisis': {
                'trust': 0.15, 'respect': 0.1, 'affection': 0.1, 'dependency': 0.05
            },
            'betrayed_trust': {
                'trust': -0.4, 'respect': -0.2, 'affection': -0.3, 'fear': 0.1
            },
            'shared_resources': {
                'trust': 0.08, 'affection': 0.06, 'dependency': 0.03
            },
            'competed_for_leadership': {
                'respect': 0.05, 'fear': 0.03, 'trust': -0.05
            },
            'saved_from_danger': {
                'trust': 0.25, 'respect': 0.2, 'affection': 0.2, 'dependency': 0.15
            },
            'public_humiliation': {
                'respect': -0.3, 'affection': -0.2, 'fear': 0.1
            },
            'kept_secret': {
                'trust': 0.2, 'affection': 0.1
            },
            'broke_promise': {
                'trust': -0.25, 'respect': -0.1, 'affection': -0.15
            },
            'showed_vulnerability': {
                'affection': 0.1, 'trust': 0.05, 'fear': -0.05
            },
            'demonstrated_competence': {
                'respect': 0.15, 'trust': 0.05
            }
        }
        
        if event_type not in relationship_events:
            available = ', '.join(relationship_events.keys())
            raise ValueError(f"Unknown event type: {event_type}. Available: {available}")
        
        changes = relationship_events[event_type]
        for dimension, base_change in changes.items():
            actual_change = base_change * impact_strength
            self.update_dimension(dimension, actual_change, reason=event_type)
    
    def get_recent_changes(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent relationship changes"""
        return self.relationship_history[-limit:] if self.relationship_history else []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'trust': self.trust,
            'respect': self.respect,
            'affection': self.affection,
            'dependency': self.dependency,
            'fear': self.fear,
            'relationship_history': self.relationship_history
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RelationshipDimensions':
        """Create from dictionary"""
        return cls(
            trust=data.get('trust', 0.5),
            respect=data.get('respect', 0.5),
            affection=data.get('affection', 0.5),
            dependency=data.get('dependency', 0.0),
            fear=data.get('fear', 0.0),
            relationship_history=data.get('relationship_history', [])
        )


@dataclass
class RelationshipMatrix:
    """Manages all relationships for one NPC"""
    
    # Main relationships storage: {target_npc_id: RelationshipDimensions}
    relationships: Dict[str, RelationshipDimensions] = field(default_factory=dict)
    
    def get_relationship(self, target_npc_id: str) -> RelationshipDimensions:
        """Get relationship with another NPC, creating neutral if doesn't exist"""
        if target_npc_id not in self.relationships:
            self.relationships[target_npc_id] = RelationshipDimensions()
        return self.relationships[target_npc_id]
    
    def update_relationship(self, target_npc_id: str, dimension: str, 
                          change: float, reason: str = "unknown"):
        """Update relationship dimension with another NPC"""
        relationship = self.get_relationship(target_npc_id)
        relationship.update_dimension(dimension, change, reason)
    
    def apply_relationship_event(self, target_npc_id: str, event_type: str, 
                               impact_strength: float = 1.0):
        """Apply relationship event with another NPC"""
        relationship = self.get_relationship(target_npc_id)
        relationship.apply_relationship_event(event_type, impact_strength)
    
    def get_closest_relationships(self, limit: int = 5) -> List[Tuple[str, float, str]]:
        """Get NPCs with highest closeness scores"""
        relationships = []
        for npc_id, rel in self.relationships.items():
            closeness = rel.get_closeness()
            relationship_type = rel.get_relationship_type()
            relationships.append((npc_id, closeness, relationship_type))
        
        return sorted(relationships, key=lambda x: x[1], reverse=True)[:limit]
    
    def get_most_influential_relationships(self, limit: int = 5) -> List[Tuple[str, float, str]]:
        """Get NPCs with highest influence potential"""
        relationships = []
        for npc_id, rel in self.relationships.items():
            influence = rel.get_influence_potential()
            relationship_type = rel.get_relationship_type()
            relationships.append((npc_id, influence, relationship_type))
        
        return sorted(relationships, key=lambda x: x[1], reverse=True)[:limit]
    
    def get_npcs_by_dimension(self, dimension: str, threshold: float = 0.6) -> List[Tuple[str, float]]:
        """Get NPCs above threshold for a specific dimension"""
        results = []
        for npc_id, rel in self.relationships.items():
            value = getattr(rel, dimension)
            if value >= threshold:
                results.append((npc_id, value))
        
        return sorted(results, key=lambda x: x[1], reverse=True)
    
    def get_trusted_npcs(self, threshold: float = 0.6) -> List[str]:
        """Get NPCs above trust threshold"""
        return [npc_id for npc_id, trust_level in self.get_npcs_by_dimension('trust', threshold)]
    
    def get_feared_npcs(self, threshold: float = 0.4) -> List[str]:
        """Get NPCs above fear threshold"""
        return [npc_id for npc_id, fear_level in self.get_npcs_by_dimension('fear', threshold)]
    
    def get_respected_npcs(self, threshold: float = 0.6) -> List[str]:
        """Get NPCs above respect threshold"""
        return [npc_id for npc_id, respect_level in self.get_npcs_by_dimension('respect', threshold)]
    
    def get_loved_npcs(self, threshold: float = 0.7) -> List[str]:
        """Get NPCs above affection threshold"""
        return [npc_id for npc_id, affection_level in self.get_npcs_by_dimension('affection', threshold)]
    
    def get_relationships_by_type(self) -> Dict[str, List[str]]:
        """Group NPCs by relationship type"""
        relationships_by_type = {}
        for npc_id, rel in self.relationships.items():
            rel_type = rel.get_relationship_type()
            if rel_type not in relationships_by_type:
                relationships_by_type[rel_type] = []
            relationships_by_type[rel_type].append(npc_id)
        
        return relationships_by_type
    
    def calculate_social_isolation(self) -> float:
        """Calculate how socially isolated this NPC is (0.0 = well connected, 1.0 = isolated)"""
        if not self.relationships:
            return 1.0
        
        # Calculate based on closeness and positive sentiment
        total_closeness = 0.0
        positive_relationships = 0
        
        for rel in self.relationships.values():
            closeness = rel.get_closeness()
            sentiment = rel.get_overall_sentiment()
            
            total_closeness += closeness
            if sentiment > 0.0:
                positive_relationships += 1
        
        average_closeness = total_closeness / len(self.relationships)
        positive_ratio = positive_relationships / len(self.relationships)
        
        # Isolation is inverse of social connection
        social_connection = (average_closeness + positive_ratio) / 2.0
        return 1.0 - social_connection
    
    def calculate_social_influence(self) -> float:
        """Calculate this NPC's overall social influence (0.0 to 1.0)"""
        if not self.relationships:
            return 0.0
        
        total_influence = sum(rel.get_influence_potential() for rel in self.relationships.values())
        average_influence = total_influence / len(self.relationships)
        
        # Weight by number of relationships (more relationships = more influence)
        relationship_bonus = min(1.0, len(self.relationships) / 20.0)  # Cap at 20 relationships
        
        return min(1.0, average_influence * (1.0 + relationship_bonus))
    
    def get_relationship_conflicts(self) -> List[Tuple[str, str, str]]:
        """Identify relationship conflicts (high fear + high dependency, etc.)"""
        conflicts = []
        
        for npc_id, rel in self.relationships.items():
            # Fear + Dependency conflict
            if rel.fear > 0.6 and rel.dependency > 0.6:
                conflicts.append((npc_id, "fear_dependency", "Fears someone they depend on"))
            
            # Love + Distrust conflict
            if rel.affection > 0.7 and rel.trust < 0.3:
                conflicts.append((npc_id, "love_distrust", "Loves someone they don't trust"))
            
            # Respect + Fear conflict
            if rel.respect > 0.7 and rel.fear > 0.6:
                conflicts.append((npc_id, "respect_fear", "Respects someone they fear"))
        
        return conflicts
    
    def get_relationship_summary(self) -> Dict[str, Any]:
        """Get comprehensive relationship summary"""
        if not self.relationships:
            return {
                'total_relationships': 0,
                'social_isolation': 1.0,
                'social_influence': 0.0,
                'relationship_distribution': {},
                'conflicts': []
            }
        
        relationships_by_type = self.get_relationships_by_type()
        closest = self.get_closest_relationships(3)
        most_influential = self.get_most_influential_relationships(3)
        conflicts = self.get_relationship_conflicts()
        
        # Calculate sentiment distribution
        sentiments = [rel.get_overall_sentiment() for rel in self.relationships.values()]
        positive_count = sum(1 for s in sentiments if s > 0.2)
        negative_count = sum(1 for s in sentiments if s < -0.2)
        neutral_count = len(sentiments) - positive_count - negative_count
        
        return {
            'total_relationships': len(self.relationships),
            'social_isolation': self.calculate_social_isolation(),
            'social_influence': self.calculate_social_influence(),
            'relationship_distribution': relationships_by_type,
            'closest_relationships': [(npc_id, closeness, rel_type) for npc_id, closeness, rel_type in closest],
            'most_influential': [(npc_id, influence, rel_type) for npc_id, influence, rel_type in most_influential],
            'sentiment_distribution': {
                'positive': positive_count,
                'neutral': neutral_count,
                'negative': negative_count
            },
            'conflicts': conflicts,
            'trust_network_size': len(self.get_trusted_npcs()),
            'fear_targets': len(self.get_feared_npcs())
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            npc_id: rel.to_dict() 
            for npc_id, rel in self.relationships.items()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RelationshipMatrix':
        """Create from dictionary"""
        matrix = cls()
        for npc_id, rel_data in data.items():
            matrix.relationships[npc_id] = RelationshipDimensions.from_dict(rel_data)
        return matrix
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, json_str: str) -> 'RelationshipMatrix':
        """Create from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)


# =============================================================================
# Relationship simulation helpers
# =============================================================================

def simulate_relationship_evolution(matrix: RelationshipMatrix, target_npc: str, 
                                  events: List[str], days_passed: int = 1) -> RelationshipMatrix:
    """Simulate relationship evolution over time with events"""
    # Apply events
    for event in events:
        matrix.apply_relationship_event(target_npc, event)
    
    # Apply time-based relationship decay/stabilization
    relationship = matrix.get_relationship(target_npc)
    
    # Extreme values tend to moderate over time (unless reinforced)
    decay_rate = 0.01 * days_passed
    
    # Trust and respect decay slowly toward neutral
    if relationship.trust > 0.7:
        relationship.update_dimension('trust', -decay_rate * 0.5, reason="time_decay")
    elif relationship.trust < 0.3:
        relationship.update_dimension('trust', decay_rate * 0.3, reason="time_healing")
    
    # Fear decays faster than other emotions
    if relationship.fear > 0.1:
        relationship.update_dimension('fear', -decay_rate * 2.0, reason="fear_decay")
    
    # Dependency can build or decay based on circumstances
    if relationship.dependency > 0.8:
        relationship.update_dimension('dependency', -decay_rate * 0.3, reason="independence_growth")
    
    return matrix


def create_random_relationship() -> RelationshipDimensions:
    """Create a random relationship for testing"""
    return RelationshipDimensions(
        trust=random.uniform(0.0, 1.0),
        respect=random.uniform(0.0, 1.0),
        affection=random.uniform(0.0, 1.0),
        dependency=random.uniform(0.0, 0.5),  # Lower average dependency
        fear=random.uniform(0.0, 0.3)        # Lower average fear
    )