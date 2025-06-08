from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any, Optional
import json
from src.utils.action_definitions import ActionType


@dataclass
class ExperienceLevels:
    """Tracks skill levels gained through actions and outcomes"""
    
    # Experience categories (0.0 - 1.0)
    leadership: float = 0.0        # Leading groups, making decisions for others
    negotiation: float = 0.0       # Successful persuasion, conflict resolution
    resource_management: float = 0.0  # Gathering, crafting, managing supplies
    crafting: float = 0.0          # Creating tools, building structures
    social_manipulation: float = 0.0  # Reading people, deception, influence
    survival: float = 0.0          # Basic survival skills, threat avoidance
    combat: float = 0.0            # Fighting, defense, intimidation
    
    # Track experience gain history for analysis
    experience_history: List[Dict[str, Any]] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate experience values"""
        for exp_name, value in self._get_experience_dict().items():
            if not isinstance(value, (int, float)):
                raise ValueError(f"{exp_name} must be a number, got {type(value)}")
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{exp_name} must be between 0.0 and 1.0, got {value}")
    
    def _get_experience_dict(self) -> Dict[str, float]:
        """Get only the experience values, not the history"""
        return {
            'leadership': self.leadership,
            'negotiation': self.negotiation,
            'resource_management': self.resource_management,
            'crafting': self.crafting,
            'social_manipulation': self.social_manipulation,
            'survival': self.survival,
            'combat': self.combat
        }
    
    def gain_experience(self, category: str, amount: float, 
                       source: str = "unknown", success: bool = True) -> bool:
        """Add experience in a category, returns True if level increased significantly"""
        if category not in self._get_experience_dict():
            available = ', '.join(self._get_experience_dict().keys())
            raise ValueError(f"Unknown experience category: {category}. Available: {available}")
        
        if amount < 0:
            raise ValueError(f"Experience amount must be positive, got {amount}")
        
        old_level = getattr(self, category)
        
        # Apply diminishing returns - harder to improve at higher levels
        diminishing_factor = 1.0 - (old_level * 0.3)  # 30% reduction at max level
        actual_gain = amount * diminishing_factor
        
        new_level = min(1.0, old_level + actual_gain)
        setattr(self, category, new_level)
        
        # Record experience gain for analysis
        self.experience_history.append({
            'category': category,
            'amount_attempted': amount,
            'amount_gained': new_level - old_level,
            'source': source,
            'success': success,
            'old_level': old_level,
            'new_level': new_level
        })
        
        # Significant improvement threshold
        significant_threshold = 0.05
        return (new_level - old_level) >= significant_threshold
    
    def gain_experience_from_action(self, action: ActionType, success: bool = True) -> List[str]:
        """Gain experience based on an action and its outcome"""
        experience_gained = []
        
        # Get experience mappings for this action
        action_mappings = EXPERIENCE_MAPPINGS.get(action, {})
        
        for category, base_amount in action_mappings.items():
            # Success affects experience gain
            success_multiplier = 1.0 if success else 0.3  # Still learn from failure
            actual_amount = base_amount * success_multiplier
            
            # Always add to gained list if there was any experience gain
            if actual_amount > 0:
                self.gain_experience(
                    category, actual_amount, 
                    source=f"action_{action.value}", success=success
                )
                experience_gained.append(category)
        
    def gain_experience_from_action(self, action: ActionType, success: bool = True) -> Dict[str, bool]:
        """Gain experience based on an action and its outcome
        
        Returns:
            Dict with categories as keys and whether the gain was significant as values
        """
        experience_results = {}
        
        # Get experience mappings for this action
        action_mappings = EXPERIENCE_MAPPINGS.get(action, {})
        
        for category, base_amount in action_mappings.items():
            # Success affects experience gain
            success_multiplier = 1.0 if success else 0.3  # Still learn from failure
            actual_amount = base_amount * success_multiplier
            
            # Always gain experience if there's any amount
            if actual_amount > 0:
                significant = self.gain_experience(
                    category, actual_amount, 
                    source=f"action_{action.value}", success=success
                )
                experience_results[category] = significant
        
        return experience_results
    
    def get_experience_categories_from_action(self, action: ActionType) -> List[str]:
        """Get list of categories that would gain experience from an action (without applying)"""
        action_mappings = EXPERIENCE_MAPPINGS.get(action, {})
        return list(action_mappings.keys())
    
    def get_experience(self, category: str) -> float:
        """Get experience level for a category"""
        if category not in self._get_experience_dict():
            raise ValueError(f"Unknown experience category: {category}")
        return getattr(self, category)
    
    def get_skill_level_description(self, category: str) -> str:
        """Get human-readable skill level"""
        level = self.get_experience(category)
        
        if level < 0.1:
            return "Novice"
        elif level < 0.3:
            return "Beginner"
        elif level < 0.5:
            return "Intermediate"
        elif level < 0.7:
            return "Advanced"
        elif level < 0.9:
            return "Expert"
        else:
            return "Master"
    
    def get_top_skills(self, limit: int = 3) -> List[Tuple[str, float, str]]:
        """Get top N skills as (skill_name, level, description) tuples"""
        experience_dict = self._get_experience_dict()
        skills = [
            (name, value, self.get_skill_level_description(name)) 
            for name, value in experience_dict.items()
        ]
        return sorted(skills, key=lambda x: x[1], reverse=True)[:limit]
    
    def get_skills_above_threshold(self, threshold: float = 0.5) -> Dict[str, Tuple[float, str]]:
        """Get all skills above a certain level"""
        skilled_areas = {}
        experience_dict = self._get_experience_dict()
        
        for skill_name, level in experience_dict.items():
            if level >= threshold:
                description = self.get_skill_level_description(skill_name)
                skilled_areas[skill_name] = (level, description)
        
        return skilled_areas
    
    def get_experience_summary(self) -> Dict[str, Any]:
        """Get comprehensive experience summary"""
        experience_dict = self._get_experience_dict()
        
        return {
            'total_experience': sum(experience_dict.values()),
            'average_experience': sum(experience_dict.values()) / len(experience_dict),
            'top_skills': self.get_top_skills(3),
            'skilled_areas': self.get_skills_above_threshold(0.4),
            'weakest_skills': sorted(experience_dict.items(), key=lambda x: x[1])[:3],
            'experience_events': len(self.experience_history),
            'specialization_score': self._calculate_specialization()
        }
    
    def _calculate_specialization(self) -> float:
        """Calculate how specialized vs generalist this NPC is (0.0 = generalist, 1.0 = specialist)"""
        experience_dict = self._get_experience_dict()
        values = list(experience_dict.values())
        
        if not values:
            return 0.0
        
        # Standard deviation of experience levels - higher = more specialized
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        std_dev = variance ** 0.5
        
        # Normalize to 0-1 range (approximate)
        return min(1.0, std_dev * 2.0)
    
    def get_confidence_modifier(self, category: str) -> float:
        """Get confidence modifier for attempting actions in this category"""
        level = self.get_experience(category)
        
        # Confidence grows with experience but plateaus
        # 0.0 experience = 1.0 confidence (no modifier)
        # 1.0 experience = 2.0 confidence (double confidence)
        return 1.0 + level
    
    def get_competence_modifier(self, category: str) -> float:
        """Get success probability modifier for actions in this category"""
        level = self.get_experience(category)
        
        # Competence improvement is more dramatic than confidence
        # 0.0 experience = 1.0 success rate (no modifier)
        # 1.0 experience = 2.5 success rate (150% improvement)
        return 1.0 + (level * 1.5)
    
    def has_expertise_in(self, category: str, threshold: float = 0.7) -> bool:
        """Check if NPC has expertise in a category"""
        return self.get_experience(category) >= threshold
    
    def get_learning_rate(self, category: str) -> float:
        """Get current learning rate for a category (decreases with experience)"""
        level = self.get_experience(category)
        # Learning rate decreases as you get more experienced
        return 1.0 - (level * 0.5)  # 50% slower learning at max level
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'experience_levels': self._get_experience_dict(),
            'experience_history': self.experience_history
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExperienceLevels':
        """Create from dictionary"""
        experience_levels = data.get('experience_levels', {})
        experience_history = data.get('experience_history', [])
        
        instance = cls(**experience_levels)
        instance.experience_history = experience_history
        return instance
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, json_str: str) -> 'ExperienceLevels':
        """Create from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)


# =============================================================================
# Experience gain mappings for different actions
# =============================================================================

EXPERIENCE_MAPPINGS = {
    # Resource Actions
    ActionType.GATHER_FOOD: {
        'survival': 0.02,
        'resource_management': 0.015
    },
    ActionType.GATHER_MATERIALS: {
        'survival': 0.01,
        'resource_management': 0.025
    },
    ActionType.CRAFT_TOOLS: {
        'crafting': 0.03,
        'resource_management': 0.01
    },
    ActionType.BUILD_SHELTER: {
        'crafting': 0.025,
        'survival': 0.015,
        'resource_management': 0.01
    },
    
    # Social Actions
    ActionType.HELP_RANDOM_NPC: {
        'social_manipulation': 0.01,
        'negotiation': 0.01,
        'leadership': 0.005
    },
    ActionType.SHARE_RESOURCES: {
        'negotiation': 0.01,
        'leadership': 0.005,
        'resource_management': 0.005
    },
    ActionType.START_CONVERSATION: {
        'social_manipulation': 0.015,
        'negotiation': 0.01
    },
    ActionType.FORM_ALLIANCE: {
        'negotiation': 0.025,
        'social_manipulation': 0.015,
        'leadership': 0.015
    },
    
    # Governance Actions
    ActionType.VOTE_ON_PROPOSAL: {
        'leadership': 0.005
    },
    ActionType.PROPOSE_NEW_RULE: {
        'leadership': 0.03,
        'negotiation': 0.015
    },
    ActionType.CHALLENGE_LEADERSHIP: {
        'leadership': 0.04,
        'combat': 0.01,
        'social_manipulation': 0.01
    },
    ActionType.SUPPORT_LEADER: {
        'leadership': 0.01,
        'negotiation': 0.005
    },
    
    # Personal Actions
    ActionType.PRACTICE_SKILLS: {
        # This is special - randomly improves a skill
        'leadership': 0.01,
        'crafting': 0.01,
        'survival': 0.01
    },
    ActionType.OBSERVE_OTHERS: {
        'social_manipulation': 0.02,
        'leadership': 0.005
    },
    
    # Combat/Conflict (when implemented)
    # ActionType.FIGHT: {
    #     'combat': 0.05,
    #     'survival': 0.01
    # }
}


# =============================================================================
# Experience-based skill checks
# =============================================================================

def calculate_action_success_probability(base_rate: float, experience_level: float) -> float:
    """Calculate success probability based on base rate and experience"""
    competence_modifier = 1.0 + (experience_level * 1.5)
    adjusted_rate = base_rate * competence_modifier
    
    # Cap at 95% to maintain some uncertainty
    return min(0.95, adjusted_rate)


def get_relevant_experience_for_action(action: ActionType, experience: ExperienceLevels) -> Tuple[str, float]:
    """Get the most relevant experience category and level for an action"""
    action_mappings = EXPERIENCE_MAPPINGS.get(action, {})
    
    if not action_mappings:
        return "survival", 0.0  # Default fallback
    
    # Find the experience category with highest relevance for this action
    best_category = max(action_mappings.keys(), key=lambda cat: action_mappings[cat])
    experience_level = experience.get_experience(best_category)
    
    return best_category, experience_level