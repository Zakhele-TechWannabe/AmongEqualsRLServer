from dataclasses import dataclass
from typing import Dict
import random
import json


@dataclass
class PersonalityTraits:
    """Core personality traits that influence behavior"""
    
    # Primary traits (0.0 - 1.0)
    greed: float = 0.5           # Resource hoarding vs sharing
    sociability: float = 0.5     # Social interaction preference
    laziness: float = 0.5        # Work avoidance
    ambition: float = 0.5        # Leadership/power seeking
    forgiveness: float = 0.5     # Ability to forgive betrayals
    courage: float = 0.5         # Risk-taking, facing threats
    analytical: float = 0.5      # Logical vs emotional decisions
    impulsiveness: float = 0.5   # Quick decisions vs deliberation
    
    def __post_init__(self):
        """Validate trait values are in valid range"""
        for trait_name, value in self.__dict__.items():
            if not isinstance(value, (int, float)):
                raise ValueError(f"{trait_name} must be a number, got {type(value)}")
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{trait_name} must be between 0.0 and 1.0, got {value}")
    
    @classmethod
    def generate_random(cls) -> 'PersonalityTraits':
        """Generate random personality for new NPC"""
        return cls(
            greed=random.uniform(0.0, 1.0),
            sociability=random.uniform(0.0, 1.0),
            laziness=random.uniform(0.0, 1.0),
            ambition=random.uniform(0.0, 1.0),
            forgiveness=random.uniform(0.0, 1.0),
            courage=random.uniform(0.0, 1.0),
            analytical=random.uniform(0.0, 1.0),
            impulsiveness=random.uniform(0.0, 1.0)
        )
    
    @classmethod
    def from_archetype(cls, archetype: str) -> 'PersonalityTraits':
        """Create personality from predefined archetype for testing"""
        archetypes = {
            'greedy_loner': cls(greed=0.9, sociability=0.2, ambition=0.3, forgiveness=0.1),
            'social_leader': cls(greed=0.2, sociability=0.9, ambition=0.8, forgiveness=0.7),
            'lazy_follower': cls(greed=0.4, sociability=0.6, laziness=0.9, ambition=0.1),
            'analytical_planner': cls(greed=0.3, sociability=0.4, analytical=0.9, impulsiveness=0.1),
            'traumatized_survivor': cls(greed=0.7, sociability=0.2, courage=0.3, forgiveness=0.2),
            'balanced_human': cls()  # All traits at 0.5 (default)
        }
        
        if archetype not in archetypes:
            available = ', '.join(archetypes.keys())
            raise ValueError(f"Unknown archetype: {archetype}. Available: {available}")
        return archetypes[archetype]
    
    def get_trait(self, trait_name: str) -> float:
        """Get trait value by name"""
        if not hasattr(self, trait_name):
            raise ValueError(f"Unknown trait: {trait_name}")
        return getattr(self, trait_name)
    
    def set_trait(self, trait_name: str, value: float) -> None:
        """Set trait value by name with validation"""
        if not hasattr(self, trait_name):
            raise ValueError(f"Unknown trait: {trait_name}")
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"Trait value must be between 0.0 and 1.0, got {value}")
        setattr(self, trait_name, value)
    
    def get_dominant_traits(self, threshold: float = 0.7) -> Dict[str, float]:
        """Get traits that are significantly high"""
        dominant = {}
        for trait_name, value in self.to_dict().items():
            if value >= threshold:
                dominant[trait_name] = value
        return dominant
    
    def get_weak_traits(self, threshold: float = 0.3) -> Dict[str, float]:
        """Get traits that are significantly low"""
        weak = {}
        for trait_name, value in self.to_dict().items():
            if value <= threshold:
                weak[trait_name] = value
        return weak
    
    def get_personality_summary(self) -> str:
        """Generate human-readable personality description"""
        dominant = self.get_dominant_traits()
        weak = self.get_weak_traits()
        
        summary_parts = []
        
        # Describe dominant traits
        if 'greed' in dominant:
            summary_parts.append("hoards resources")
        if 'sociability' in dominant:
            summary_parts.append("very social")
        if 'laziness' in dominant:
            summary_parts.append("avoids work")
        if 'ambition' in dominant:
            summary_parts.append("seeks leadership")
        if 'forgiveness' in dominant:
            summary_parts.append("very forgiving")
        if 'courage' in dominant:
            summary_parts.append("brave")
        if 'analytical' in dominant:
            summary_parts.append("logical thinker")
        if 'impulsiveness' in dominant:
            summary_parts.append("acts quickly")
        
        # Describe weak traits
        if 'sociability' in weak:
            summary_parts.append("antisocial")
        if 'courage' in weak:
            summary_parts.append("cowardly")
        if 'forgiveness' in weak:
            summary_parts.append("holds grudges")
        if 'analytical' in weak:
            summary_parts.append("emotional decision-maker")
        
        if not summary_parts:
            return "balanced personality"
        
        return ", ".join(summary_parts)
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary for serialization"""
        return {
            'greed': self.greed,
            'sociability': self.sociability,
            'laziness': self.laziness,
            'ambition': self.ambition,
            'forgiveness': self.forgiveness,
            'courage': self.courage,
            'analytical': self.analytical,
            'impulsiveness': self.impulsiveness
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> 'PersonalityTraits':
        """Create from dictionary"""
        return cls(**data)
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, json_str: str) -> 'PersonalityTraits':
        """Create from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)