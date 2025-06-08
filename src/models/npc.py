from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any, Optional
import json
import random
from datetime import datetime

from .personality import PersonalityTraits
from .experience import ExperienceLevels
from .trauma import TraumaState, create_common_trauma
from .relationships import RelationshipMatrix
from ..utils.action_definitions import ActionType


@dataclass
class NPCState:
    """Complete NPC with integrated personality, experience, trauma, and relationships"""
    
    # Core Identity
    npc_id: str
    name: str = ""
    age: int = 25
    
    # Physical State (0.0 - 1.0)
    health: float = 0.8
    hunger_level: float = 0.5      # 0.0 = well fed, 1.0 = starving
    energy_level: float = 0.7      # 0.0 = exhausted, 1.0 = fully rested
    
    # Psychological Systems
    personality: PersonalityTraits = field(default_factory=PersonalityTraits)
    experience: ExperienceLevels = field(default_factory=ExperienceLevels)
    trauma: TraumaState = field(default_factory=TraumaState)
    relationships: RelationshipMatrix = field(default_factory=RelationshipMatrix)
    
    # Game State
    last_action: Optional[str] = None
    last_action_success: Optional[bool] = None
    days_alive: int = 0
    
    # Internal tracking
    creation_timestamp: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate NPC state after creation"""
        if self.age < 0:
            raise ValueError("Age cannot be negative")
        
        physical_stats = ['health', 'hunger_level', 'energy_level']
        for stat in physical_stats:
            value = getattr(self, stat)
            if not isinstance(value, (int, float)):
                raise ValueError(f"{stat} must be a number, got {type(value)}")
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{stat} must be between 0.0 and 1.0, got {value}")
        
        if not self.name:
            self.name = f"NPC_{self.npc_id}"
    
    @classmethod
    def create_random_npc(cls, npc_id: str, name: str = "", age_range: Tuple[int, int] = (18, 60)) -> 'NPCState':
        """Create a random NPC with varied characteristics"""
        age = random.randint(*age_range)
        
        npc = cls(
            npc_id=npc_id,
            name=name or f"NPC_{npc_id}",
            age=age,
            health=random.uniform(0.6, 1.0),
            hunger_level=random.uniform(0.1, 0.7),
            energy_level=random.uniform(0.4, 0.9),
            personality=PersonalityTraits.generate_random(),
            experience=ExperienceLevels(),
            trauma=TraumaState(),
            relationships=RelationshipMatrix()
        )
        
        # Add some random life experiences based on age
        npc._generate_life_history()
        
        return npc
    
    @classmethod
    def create_npc_with_archetype(cls, npc_id: str, archetype: str, name: str = "", age: int = 25) -> 'NPCState':
        """Create NPC with specific personality archetype"""
        npc = cls(
            npc_id=npc_id,
            name=name or f"{archetype}_{npc_id}",
            age=age,
            personality=PersonalityTraits.from_archetype(archetype)
        )
        
        # Add appropriate life experiences for archetype
        npc._generate_archetype_history(archetype)
        
        return npc
    
    def _generate_life_history(self):
        """Generate random life experiences based on age"""
        # Older NPCs have more experience and potentially more trauma
        experience_multiplier = min(2.0, self.age / 30.0)
        trauma_probability = min(0.6, self.age / 50.0)
        
        # Add some random experience
        skill_categories = ['leadership', 'negotiation', 'survival', 'crafting', 'resource_management']
        for category in skill_categories:
            if random.random() < 0.4:  # 40% chance to have experience in each category
                amount = random.uniform(0.05, 0.3) * experience_multiplier
                self.experience.gain_experience(category, amount, source="life_history")
        
        # Potentially add trauma
        if random.random() < trauma_probability:
            trauma_types = ['betrayal', 'social_rejection', 'resource_loss', 'leadership_failure']
            trauma_type = random.choice(trauma_types)
            severity = random.choice(['mild', 'moderate', 'severe'])
            trauma_age = random.randint(max(5, self.age - 20), self.age - 1)
            
            trauma_memory = create_common_trauma(trauma_type, severity, trauma_age)
            self.trauma.memories.append(trauma_memory)
            
            # Apply some natural healing
            days_since = (self.age - trauma_age) * 365
            self.trauma.apply_daily_healing(self.personality, days_since)
    
    def _generate_archetype_history(self, archetype: str):
        """Generate appropriate history for personality archetype"""
        archetype_experiences = {
            'social_leader': {
                'experience': [('leadership', 0.4), ('negotiation', 0.3), ('social_manipulation', 0.2)],
                'potential_trauma': [('leadership_failure', 'moderate')]
            },
            'greedy_loner': {
                'experience': [('resource_management', 0.5), ('survival', 0.3)],
                'potential_trauma': [('betrayal', 'severe'), ('social_rejection', 'moderate')]
            },
            'analytical_planner': {
                'experience': [('crafting', 0.4), ('resource_management', 0.3), ('leadership', 0.2)],
                'potential_trauma': [('leadership_failure', 'mild')]
            },
            'traumatized_survivor': {
                'experience': [('survival', 0.6), ('resource_management', 0.4)],
                'potential_trauma': [('violence', 'severe'), ('abandonment', 'moderate')]
            }
        }
        
        if archetype in archetype_experiences:
            config = archetype_experiences[archetype]
            
            # Add appropriate experience
            for category, amount in config['experience']:
                self.experience.gain_experience(category, amount, source=f"archetype_{archetype}")
            
            # Add characteristic trauma
            for trauma_type, severity in config['potential_trauma']:
                if random.random() < 0.7:  # 70% chance
                    trauma_age = random.randint(max(5, self.age - 15), self.age - 1)
                    trauma_memory = create_common_trauma(trauma_type, severity, trauma_age)
                    self.trauma.memories.append(trauma_memory)
                    
                    # Apply natural healing
                    days_since = (self.age - trauma_age) * 365
                    self.trauma.apply_daily_healing(self.personality, days_since)
    
    # ==========================================================================
    # Physical State Management
    # ==========================================================================
    
    def update_physical_state(self, health_change: float = 0.0, hunger_change: float = 0.0, 
                            energy_change: float = 0.0):
        """Update physical statistics with validation"""
        self.health = max(0.0, min(1.0, self.health + health_change))
        self.hunger_level = max(0.0, min(1.0, self.hunger_level + hunger_change))
        self.energy_level = max(0.0, min(1.0, self.energy_level + energy_change))
    
    def get_physical_condition(self) -> str:
        """Get human-readable physical condition"""
        if self.health < 0.2:
            return "critically injured"
        elif self.health < 0.5:
            return "injured"
        elif self.hunger_level > 0.8:
            return "starving"
        elif self.hunger_level > 0.6:
            return "very hungry"
        elif self.energy_level < 0.2:
            return "exhausted"
        elif self.energy_level < 0.4:
            return "tired"
        else:
            return "healthy"
    
    def needs_immediate_attention(self) -> List[str]:
        """Get list of urgent physical needs"""
        urgent_needs = []
        
        if self.health < 0.3:
            urgent_needs.append("medical_attention")
        if self.hunger_level > 0.7:
            urgent_needs.append("food")
        if self.energy_level < 0.2:
            urgent_needs.append("rest")
        
        return urgent_needs
    
    # ==========================================================================
    # Action Processing
    # ==========================================================================
    
    def perform_action(self, action: ActionType, success: bool, outcome_data: Dict[str, Any] = None):
        """Process the results of an action"""
        self.last_action = action.value
        self.last_action_success = success
        
        outcome_data = outcome_data or {}
        
        # Gain experience from action
        experience_results = self.experience.gain_experience_from_action(action, success)
        
        # Update physical state based on action
        self._apply_action_physical_effects(action, success, outcome_data)
        
        # Update relationships if action involved other NPCs
        if 'target_npc' in outcome_data:
            self._apply_action_relationship_effects(action, success, outcome_data)
        
        # Check for traumatic events
        if 'traumatic_event' in outcome_data:
            self._process_traumatic_event(outcome_data['traumatic_event'])
        
        return experience_results
    
    def _apply_action_physical_effects(self, action: ActionType, success: bool, outcome_data: Dict):
        """Apply physical effects of actions"""
        from ..utils.action_definitions import get_action_metadata
        
        metadata = get_action_metadata(action)
        energy_cost = metadata.get('energy_cost', 0.1)
        
        # Apply energy cost
        self.update_physical_state(energy_change=-energy_cost)
        
        # Specific action effects
        if action == ActionType.GATHER_FOOD and success:
            hunger_reduction = outcome_data.get('food_gained', 0.1)
            self.update_physical_state(hunger_change=-hunger_reduction)
        
        elif action == ActionType.REST:
            energy_restoration = 0.4 if success else 0.2
            health_restoration = 0.1 if self.health < 0.8 else 0.0
            self.update_physical_state(energy_change=energy_restoration, health_change=health_restoration)
        
        elif action in [ActionType.BUILD_SHELTER, ActionType.CRAFT_TOOLS] and success:
            # Physical work improves health slightly
            self.update_physical_state(health_change=0.02)
    
    def _apply_action_relationship_effects(self, action: ActionType, success: bool, outcome_data: Dict):
        """Apply relationship effects of social actions"""
        target_npc = outcome_data.get('target_npc')
        if not target_npc:
            return
        
        # Map actions to relationship events
        action_relationship_map = {
            ActionType.HELP_RANDOM_NPC: 'helped_in_crisis' if success else 'failed_to_help',
            ActionType.SHARE_RESOURCES: 'shared_resources' if success else 'refused_sharing',
            ActionType.FORM_ALLIANCE: 'formed_alliance' if success else 'rejected_alliance',
            ActionType.START_CONVERSATION: 'positive_interaction' if success else 'awkward_interaction'
        }
        
        # Apply relationship changes
        if action in action_relationship_map:
            event_type = action_relationship_map[action]
            
            # Custom events for specific actions
            if event_type == 'helped_in_crisis':
                self.relationships.apply_relationship_event(target_npc, 'helped_in_crisis')
            elif event_type == 'shared_resources':
                self.relationships.apply_relationship_event(target_npc, 'shared_resources')
            elif event_type == 'formed_alliance':
                self.relationships.update_relationship(target_npc, 'trust', 0.1, 'formed_alliance')
                self.relationships.update_relationship(target_npc, 'respect', 0.05, 'formed_alliance')
            elif event_type == 'positive_interaction':
                self.relationships.update_relationship(target_npc, 'affection', 0.05, 'conversation')
    
    def _process_traumatic_event(self, trauma_data: Dict):
        """Process a traumatic event"""
        trauma_type = trauma_data.get('type', 'generic')
        impact = trauma_data.get('impact', 0.5)
        description = trauma_data.get('description', f"Experienced {trauma_type}")
        related_npcs = trauma_data.get('related_npcs', [])
        
        self.trauma.add_trauma(trauma_type, impact, self.age, description, related_npcs)
    
    # ==========================================================================
    # Social Interactions
    # ==========================================================================
    
    def interact_with_npc(self, target_npc_id: str, interaction_type: str, 
                         outcome: str = "success") -> Dict[str, Any]:
        """Handle direct interaction with another NPC"""
        
        interaction_effects = {
            'casual_conversation': {
                'success': {'affection': 0.05, 'trust': 0.02},
                'failure': {'affection': -0.02}
            },
            'help_request': {
                'success': {'trust': 0.1, 'dependency': 0.05, 'affection': 0.08},
                'failure': {'trust': -0.05, 'respect': -0.03}
            },
            'resource_sharing': {
                'success': {'trust': 0.08, 'affection': 0.06, 'dependency': 0.03},
                'failure': {'trust': -0.1, 'affection': -0.05}
            },
            'conflict': {
                'success': {'fear': 0.1, 'respect': 0.05, 'affection': -0.1},
                'failure': {'fear': -0.05, 'respect': -0.1, 'trust': -0.05}
            },
            'betrayal': {
                'success': {'trust': -0.4, 'affection': -0.3, 'fear': 0.2, 'respect': -0.2}
            }
        }
        
        if interaction_type not in interaction_effects:
            return {'error': f"Unknown interaction type: {interaction_type}"}
        
        effects = interaction_effects[interaction_type].get(outcome, {})
        
        # Apply relationship changes
        for dimension, change in effects.items():
            self.relationships.update_relationship(
                target_npc_id, dimension, change, 
                reason=f"{interaction_type}_{outcome}"
            )
        
        # Special handling for traumatic interactions
        if interaction_type == 'betrayal' and outcome == 'success':
            self._process_traumatic_event({
                'type': 'betrayal',
                'impact': 0.6,
                'description': f"Betrayed by {target_npc_id}",
                'related_npcs': [target_npc_id]
            })
        
        return {
            'interaction_type': interaction_type,
            'outcome': outcome,
            'relationship_changes': effects,
            'new_relationship_type': self.relationships.get_relationship(target_npc_id).get_relationship_type()
        }
    
    # ==========================================================================
    # Daily Life Simulation
    # ==========================================================================
    
    def advance_day(self, activities: List[str] = None):
        """Advance one day in the NPC's life"""
        self.days_alive += 1
        activities = activities or []
        
        # Natural daily changes
        self.update_physical_state(
            hunger_change=random.uniform(0.1, 0.2),  # Get hungrier
            energy_change=random.uniform(-0.1, 0.1)  # Variable energy
        )
        
        # Apply daily healing
        self.trauma.apply_daily_healing(self.personality, days_passed=1)
        
        # Process healing activities
        for activity in activities:
            if activity in ['meditation', 'socializing', 'crafting', 'prayer', 'helping_others']:
                healing_amount = random.uniform(0.005, 0.02)
                self.trauma.apply_activity_healing(activity, healing_amount, self.personality)
        
        # Age-related changes (very gradual)
        if self.days_alive % 365 == 0:  # Once per year
            self.age += 1
            
            # Slight wisdom gain from life experience
            if random.random() < 0.3:
                skill = random.choice(['leadership', 'negotiation', 'survival'])
                self.experience.gain_experience(skill, 0.01, source="life_wisdom")
    
    # ==========================================================================
    # Analysis and Summary
    # ==========================================================================
    
    def get_character_summary(self) -> Dict[str, Any]:
        """Get comprehensive character summary"""
        personality_summary = self.personality.get_personality_summary()
        experience_summary = self.experience.get_experience_summary()
        trauma_summary = self.trauma.get_trauma_summary()
        relationship_summary = self.relationships.get_relationship_summary()
        
        return {
            'basic_info': {
                'id': self.npc_id,
                'name': self.name,
                'age': self.age,
                'days_alive': self.days_alive,
                'physical_condition': self.get_physical_condition(),
                'urgent_needs': self.needs_immediate_attention()
            },
            'personality': {
                'summary': personality_summary,
                'dominant_traits': self.personality.get_dominant_traits(),
                'weak_traits': self.personality.get_weak_traits()
            },
            'experience': {
                'total_experience': experience_summary['total_experience'],
                'top_skills': experience_summary['top_skills'],
                'specialization': experience_summary['specialization_score']
            },
            'trauma': {
                'trauma_count': trauma_summary['total_trauma_count'],
                'most_severe': trauma_summary['most_severe'],
                'healing_progress': trauma_summary['healing_progress'],
                'behavioral_influences': self.trauma.get_trauma_influence_on_behavior()
            },
            'relationships': {
                'total_relationships': relationship_summary['total_relationships'],
                'social_isolation': relationship_summary['social_isolation'],
                'social_influence': relationship_summary['social_influence'],
                'closest_relationships': relationship_summary.get('closest_relationships', [])[:3],
                'conflicts': relationship_summary.get('conflicts', [])
            },
            'recent_activity': {
                'last_action': self.last_action,
                'last_action_success': self.last_action_success
            }
        }
    
    def get_decision_context(self) -> Dict[str, Any]:
        """Get context for decision-making (used by AI agents)"""
        return {
            'physical_state': {
                'health': self.health,
                'hunger': self.hunger_level,
                'energy': self.energy_level,
                'urgent_needs': self.needs_immediate_attention()
            },
            'personality_traits': self.personality.to_dict(),
            'experience_levels': self.experience.to_dict()['experience_levels'],
            'active_traumas': self.trauma.get_active_traumas(),
            'trauma_influences': self.trauma.get_trauma_influence_on_behavior(),
            'trusted_npcs': self.relationships.get_trusted_npcs(),
            'feared_npcs': self.relationships.get_feared_npcs(),
            'social_isolation': self.relationships.calculate_social_isolation(),
            'relationship_conflicts': self.relationships.get_relationship_conflicts()
        }
    
    # ==========================================================================
    # Serialization
    # ==========================================================================
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'npc_id': self.npc_id,
            'name': self.name,
            'age': self.age,
            'health': self.health,
            'hunger_level': self.hunger_level,
            'energy_level': self.energy_level,
            'personality': self.personality.to_dict(),
            'experience': self.experience.to_dict(),
            'trauma': self.trauma.to_dict(),
            'relationships': self.relationships.to_dict(),
            'last_action': self.last_action,
            'last_action_success': self.last_action_success,
            'days_alive': self.days_alive,
            'creation_timestamp': self.creation_timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NPCState':
        """Create from dictionary"""
        npc = cls(
            npc_id=data['npc_id'],
            name=data.get('name', ''),
            age=data.get('age', 25),
            health=data.get('health', 0.8),
            hunger_level=data.get('hunger_level', 0.5),
            energy_level=data.get('energy_level', 0.7),
            last_action=data.get('last_action'),
            last_action_success=data.get('last_action_success'),
            days_alive=data.get('days_alive', 0),
            creation_timestamp=datetime.fromisoformat(
                data.get('creation_timestamp', datetime.now().isoformat())
            )
        )
        
        # Reconstruct complex objects
        if 'personality' in data:
            npc.personality = PersonalityTraits.from_dict(data['personality'])
        if 'experience' in data:
            npc.experience = ExperienceLevels.from_dict(data['experience'])
        if 'trauma' in data:
            npc.trauma = TraumaState.from_dict(data['trauma'])
        if 'relationships' in data:
            npc.relationships = RelationshipMatrix.from_dict(data['relationships'])
        
        return npc
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'NPCState':
        """Create from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)