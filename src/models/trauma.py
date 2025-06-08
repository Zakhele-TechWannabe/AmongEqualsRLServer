from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import json
import random


@dataclass
class TraumaMemory:
    """Individual traumatic experience with healing tracking"""
    
    event_type: str              # 'betrayal', 'leadership_failure', 'social_rejection', etc.
    original_impact: float       # Initial trauma intensity (0.0 - 2.0+, can exceed 1.0 for severe trauma)
    current_impact: float        # Current intensity after healing
    age_when_occurred: int       # NPC's age when trauma happened
    description: str             # What happened
    related_npcs: List[str] = field(default_factory=list)  # NPCs involved in the trauma
    healing_activities: List[str] = field(default_factory=list)  # What helped heal
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate trauma memory data"""
        if self.original_impact < 0:
            raise ValueError("Original impact cannot be negative")
        if self.current_impact < 0:
            raise ValueError("Current impact cannot be negative")
        if self.current_impact > self.original_impact:
            raise ValueError("Current impact cannot exceed original impact")
        if self.age_when_occurred < 0:
            raise ValueError("Age when occurred must be non-negative")
    
    @property
    def scar_threshold(self) -> float:
        """Minimum impact level - severe trauma never fully disappears"""
        if self.original_impact <= 0.5:
            return 0.0  # Minor trauma can heal completely
        elif self.original_impact <= 1.0:
            return self.original_impact * 0.1  # 10% scar for moderate trauma
        else:
            return self.original_impact * 0.3  # 30% scar for severe trauma
    
    @property
    def is_fully_healed(self) -> bool:
        """Check if trauma has healed as much as possible"""
        return self.current_impact <= self.scar_threshold
    
    @property
    def healing_progress(self) -> float:
        """Get healing progress as a percentage (0.0 = no healing, 1.0 = fully healed)"""
        if self.original_impact == 0:
            return 1.0
        
        max_possible_healing = self.original_impact - self.scar_threshold
        actual_healing = self.original_impact - self.current_impact
        
        if max_possible_healing == 0:
            return 1.0  # No healing possible, consider "fully healed"
        
        return min(1.0, actual_healing / max_possible_healing)
    
    def apply_healing(self, healing_amount: float, healing_source: str):
        """Apply healing from various sources"""
        if healing_amount < 0:
            raise ValueError("Healing amount must be non-negative")
        
        old_impact = self.current_impact
        self.current_impact = max(self.scar_threshold, self.current_impact - healing_amount)
        
        actual_healing = old_impact - self.current_impact
        if actual_healing > 0:
            self.healing_activities.append(f"{healing_source}:{actual_healing:.3f}")
    
    def get_intensity_description(self) -> str:
        """Get human-readable description of current trauma intensity"""
        if self.current_impact <= 0.1:
            return "minimal"
        elif self.current_impact <= 0.3:
            return "mild"
        elif self.current_impact <= 0.6:
            return "moderate"
        elif self.current_impact <= 0.9:
            return "severe"
        else:
            return "overwhelming"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'event_type': self.event_type,
            'original_impact': self.original_impact,
            'current_impact': self.current_impact,
            'age_when_occurred': self.age_when_occurred,
            'description': self.description,
            'related_npcs': self.related_npcs,
            'healing_activities': self.healing_activities,
            'timestamp': self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TraumaMemory':
        """Create from dictionary"""
        timestamp = datetime.fromisoformat(data.get('timestamp', datetime.now().isoformat()))
        
        return cls(
            event_type=data['event_type'],
            original_impact=data['original_impact'],
            current_impact=data['current_impact'],
            age_when_occurred=data['age_when_occurred'],
            description=data['description'],
            related_npcs=data.get('related_npcs', []),
            healing_activities=data.get('healing_activities', []),
            timestamp=timestamp
        )


@dataclass
class TraumaState:
    """Complete trauma state for an NPC with healing mechanisms"""
    
    memories: List[TraumaMemory] = field(default_factory=list)
    healing_progress: Dict[str, float] = field(default_factory=dict)
    last_healing_activity: Optional[str] = None
    natural_healing_rate: float = 0.001  # Base healing per day
    
    def add_trauma(self, event_type: str, impact: float, age: int, 
                  description: str, related_npcs: List[str] = None) -> TraumaMemory:
        """Add new traumatic experience"""
        if impact < 0:
            raise ValueError("Trauma impact must be non-negative")
        if age < 0:
            raise ValueError("Age must be non-negative")
        
        memory = TraumaMemory(
            event_type=event_type,
            original_impact=impact,
            current_impact=impact,
            age_when_occurred=age,
            description=description,
            related_npcs=related_npcs or []
        )
        self.memories.append(memory)
        return memory
    
    def get_trauma_impact(self, trauma_type: str) -> float:
        """Get current total impact for a trauma type"""
        total_impact = 0.0
        for memory in self.memories:
            if memory.event_type == trauma_type:
                total_impact += memory.current_impact
        return min(2.0, total_impact)  # Cap at 2.0 for extremely severe combined trauma
    
    def get_active_traumas(self, threshold: float = 0.1) -> Dict[str, float]:
        """Get all trauma types with significant impact"""
        trauma_totals = {}
        for memory in self.memories:
            if memory.current_impact >= threshold:
                if memory.event_type not in trauma_totals:
                    trauma_totals[memory.event_type] = 0.0
                trauma_totals[memory.event_type] += memory.current_impact
        
        return {k: min(2.0, v) for k, v in trauma_totals.items()}
    
    def get_trauma_memories_by_type(self, trauma_type: str) -> List[TraumaMemory]:
        """Get all memories of a specific trauma type"""
        return [memory for memory in self.memories if memory.event_type == trauma_type]
    
    def get_most_severe_trauma(self) -> Optional[TraumaMemory]:
        """Get the trauma memory with highest current impact"""
        if not self.memories:
            return None
        return max(self.memories, key=lambda m: m.current_impact)
    
    def apply_daily_healing(self, personality_traits: 'PersonalityTraits', days_passed: int = 1):
        """Apply natural healing over time based on personality"""
        # Import here to avoid circular imports
        from src.models.personality import PersonalityTraits
        
        # Personality affects healing rate
        healing_multiplier = (
            personality_traits.forgiveness * 0.5 +      # Forgiving people heal faster
            (1.0 - personality_traits.impulsiveness) * 0.3 +  # Patient people heal better
            personality_traits.analytical * 0.2 +       # Understanding helps healing
            (1.0 - personality_traits.laziness) * 0.2   # Active people engage in healing
        )
        
        daily_healing = self.natural_healing_rate * healing_multiplier * days_passed
        
        for memory in self.memories:
            if not memory.is_fully_healed:
                memory.apply_healing(daily_healing, "natural_healing")
    
    def apply_activity_healing(self, activity: str, healing_amount: float, 
                             personality_traits: 'PersonalityTraits' = None):
        """Apply healing from specific activities"""
        if healing_amount < 0:
            raise ValueError("Healing amount must be non-negative")
        
        self.last_healing_activity = activity
        
        # Different activities heal different types of trauma more effectively
        activity_effectiveness = {
            'prayer': {
                'effective_types': ['guilt', 'loss_of_purpose', 'moral_failure'],
                'general_effectiveness': 0.8
            },
            'meditation': {
                'effective_types': ['anxiety', 'leadership_failure', 'social_rejection'],
                'general_effectiveness': 0.9
            },
            'socializing': {
                'effective_types': ['social_rejection', 'isolation', 'betrayal'],
                'general_effectiveness': 0.7
            },
            'helping_others': {
                'effective_types': ['guilt', 'selfishness', 'leadership_failure'],
                'general_effectiveness': 0.8
            },
            'crafting': {
                'effective_types': ['depression', 'purposelessness', 'resource_loss'],
                'general_effectiveness': 0.6
            },
            'storytelling': {
                'effective_types': ['all'],  # Storytelling helps process all trauma
                'general_effectiveness': 1.0
            },
            'physical_exercise': {
                'effective_types': ['anxiety', 'depression', 'violence'],
                'general_effectiveness': 0.7
            }
        }
        
        activity_config = activity_effectiveness.get(activity, {
            'effective_types': [],
            'general_effectiveness': 0.5
        })
        
        for memory in self.memories:
            if not memory.is_fully_healed:
                # Check if activity is effective for this trauma type
                effective_types = activity_config['effective_types']
                base_effectiveness = activity_config['general_effectiveness']
                
                if 'all' in effective_types or memory.event_type in effective_types:
                    # Activity is specifically effective for this trauma type
                    effectiveness = base_effectiveness * 1.5
                else:
                    # General healing effect
                    effectiveness = base_effectiveness * 0.5
                
                # Apply personality modifiers if provided
                if personality_traits:
                    if activity == 'socializing' and personality_traits.sociability > 0.7:
                        effectiveness *= 1.3
                    elif activity == 'meditation' and personality_traits.analytical > 0.7:
                        effectiveness *= 1.2
                    elif activity == 'helping_others' and personality_traits.forgiveness > 0.7:
                        effectiveness *= 1.2
                
                adjusted_healing = healing_amount * effectiveness
                memory.apply_healing(adjusted_healing, f"activity_{activity}")
    
    def apply_counter_experience_healing(self, counter_event_type: str, 
                                       positive_impact: float, description: str):
        """Apply healing through positive counter-experiences"""
        if positive_impact < 0:
            raise ValueError("Positive impact must be non-negative")
        
        # Map trauma types to their counter-experiences
        counter_mappings = {
            'betrayal': ['trust_restoration', 'loyalty_demonstrated'],
            'leadership_failure': ['leadership_success', 'recognition'],
            'social_rejection': ['social_acceptance', 'friendship_formed'],
            'resource_loss': ['resource_security', 'abundance_experienced'],
            'violence': ['safety_provided', 'protection_received'],
            'abandonment': ['loyalty_shown', 'commitment_demonstrated']
        }
        
        # Find traumas that can be healed by this counter-experience
        for trauma_type, counter_types in counter_mappings.items():
            if counter_event_type in counter_types:
                trauma_memories = self.get_trauma_memories_by_type(trauma_type)
                
                for memory in trauma_memories:
                    if not memory.is_fully_healed:
                        # Counter-experiences are very effective but don't fully erase trauma
                        healing_amount = min(positive_impact * 0.6, memory.current_impact * 0.8)
                        memory.apply_healing(healing_amount, f"counter_experience_{counter_event_type}")
    
    def get_trauma_summary(self) -> Dict[str, Any]:
        """Get comprehensive trauma summary"""
        if not self.memories:
            return {
                'total_trauma_count': 0,
                'active_traumas': {},
                'most_severe': None,
                'overall_trauma_level': 0.0,
                'healing_progress': 1.0
            }
        
        active_traumas = self.get_active_traumas()
        most_severe = self.get_most_severe_trauma()
        
        # Calculate overall trauma level
        total_current_impact = sum(memory.current_impact for memory in self.memories)
        total_original_impact = sum(memory.original_impact for memory in self.memories)
        
        # Calculate overall healing progress
        overall_healing_progress = 0.0
        if total_original_impact > 0:
            total_possible_healing = sum(
                memory.original_impact - memory.scar_threshold for memory in self.memories
            )
            total_actual_healing = sum(
                memory.original_impact - memory.current_impact for memory in self.memories
            )
            if total_possible_healing > 0:
                overall_healing_progress = total_actual_healing / total_possible_healing
        
        return {
            'total_trauma_count': len(self.memories),
            'active_traumas': active_traumas,
            'most_severe': {
                'type': most_severe.event_type,
                'impact': most_severe.current_impact,
                'description': most_severe.description,
                'intensity': most_severe.get_intensity_description()
            } if most_severe else None,
            'overall_trauma_level': total_current_impact,
            'healing_progress': overall_healing_progress,
            'fully_healed_count': sum(1 for memory in self.memories if memory.is_fully_healed),
            'recent_healing_activity': self.last_healing_activity
        }
    
    def get_trauma_influence_on_behavior(self) -> Dict[str, Any]:
        """Get how trauma should influence NPC behavior"""
        active_traumas = self.get_active_traumas()
        
        behavioral_influences = {
            'trust_issues': 0.0,
            'social_withdrawal': 0.0,
            'leadership_avoidance': 0.0,
            'resource_hoarding': 0.0,
            'conflict_avoidance': 0.0,
            'risk_aversion': 0.0
        }
        
        # Map trauma types to behavioral influences
        trauma_behavior_map = {
            'betrayal': {'trust_issues': 0.8, 'social_withdrawal': 0.4},
            'leadership_failure': {'leadership_avoidance': 0.9, 'social_withdrawal': 0.3},
            'social_rejection': {'social_withdrawal': 0.8, 'trust_issues': 0.3},
            'resource_loss': {'resource_hoarding': 0.7, 'risk_aversion': 0.5},
            'violence': {'conflict_avoidance': 0.9, 'risk_aversion': 0.6},
            'abandonment': {'trust_issues': 0.6, 'social_withdrawal': 0.5}
        }
        
        for trauma_type, impact in active_traumas.items():
            if trauma_type in trauma_behavior_map:
                behaviors = trauma_behavior_map[trauma_type]
                for behavior, strength in behaviors.items():
                    behavioral_influences[behavior] += impact * strength
        
        # Cap influences at reasonable levels
        return {k: min(1.0, v) for k, v in behavioral_influences.items()}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'memories': [memory.to_dict() for memory in self.memories],
            'healing_progress': self.healing_progress,
            'last_healing_activity': self.last_healing_activity,
            'natural_healing_rate': self.natural_healing_rate
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TraumaState':
        """Create from dictionary"""
        trauma_state = cls()
        trauma_state.healing_progress = data.get('healing_progress', {})
        trauma_state.last_healing_activity = data.get('last_healing_activity')
        trauma_state.natural_healing_rate = data.get('natural_healing_rate', 0.001)
        
        # Reconstruct trauma memories
        for memory_data in data.get('memories', []):
            memory = TraumaMemory.from_dict(memory_data)
            trauma_state.memories.append(memory)
        
        return trauma_state
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, json_str: str) -> 'TraumaState':
        """Create from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)


# =============================================================================
# Trauma creation helpers
# =============================================================================

def create_common_trauma(trauma_type: str, severity: str, age: int, 
                        description: str = None, related_npcs: List[str] = None) -> TraumaMemory:
    """Create common trauma types with appropriate severity levels"""
    
    severity_impacts = {
        'mild': (0.1, 0.3),
        'moderate': (0.3, 0.6),
        'severe': (0.6, 1.0),
        'devastating': (1.0, 2.0)
    }
    
    if severity not in severity_impacts:
        raise ValueError(f"Severity must be one of: {list(severity_impacts.keys())}")
    
    min_impact, max_impact = severity_impacts[severity]
    impact = random.uniform(min_impact, max_impact)
    
    default_descriptions = {
        'betrayal': f"Was betrayed by someone they trusted at age {age}",
        'leadership_failure': f"Failed in a leadership role, causing harm to others at age {age}",
        'social_rejection': f"Was rejected or ostracized by their community at age {age}",
        'resource_loss': f"Lost important resources or security at age {age}",
        'violence': f"Experienced or witnessed violence at age {age}",
        'abandonment': f"Was abandoned by someone important at age {age}"
    }
    
    final_description = description or default_descriptions.get(trauma_type, f"Experienced {trauma_type} at age {age}")
    
    return TraumaMemory(
        event_type=trauma_type,
        original_impact=impact,
        current_impact=impact,
        age_when_occurred=age,
        description=final_description,
        related_npcs=related_npcs or []
    )