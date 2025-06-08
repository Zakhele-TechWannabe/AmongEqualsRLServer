from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
import json
import random
from datetime import datetime
from enum import Enum

from ..utils.action_definitions import ActionType


class WeatherType(Enum):
    """Weather conditions affecting settlement"""
    CLEAR = "clear"
    RAIN = "rain"
    STORM = "storm"
    DROUGHT = "drought"
    EXTREME_COLD = "extreme_cold"
    EXTREME_HEAT = "extreme_heat"


class ThreatType(Enum):
    """External threats to the settlement"""
    NONE = "none"
    WILDLIFE = "wildlife"
    RAIDERS = "raiders"
    NATURAL_DISASTER = "natural_disaster"
    RESOURCE_DEPLETION = "resource_depletion"
    DISEASE = "disease"


@dataclass
class Settlement:
    """Core settlement infrastructure and resources"""
    
    # Resource levels (raw amounts, not per capita)
    food_stores: float = 100.0
    material_stores: float = 50.0
    tool_count: int = 10
    shelter_capacity: int = 30  # How many people can be sheltered
    
    # Infrastructure quality (0.0 - 1.0)
    shelter_quality: float = 0.6
    food_storage_quality: float = 0.5  # Affects spoilage
    workshop_quality: float = 0.4      # Affects crafting efficiency
    defenses_quality: float = 0.3      # Affects protection from threats
    
    # Resource generation rates (per day)
    natural_food_generation: float = 5.0    # Foraging, hunting, etc.
    natural_material_generation: float = 3.0 # Fallen wood, stone, etc.
    
    def __post_init__(self):
        """Validate settlement values"""
        if self.food_stores < 0 or self.material_stores < 0:
            raise ValueError("Resource stores cannot be negative")
        
        quality_metrics = ['shelter_quality', 'food_storage_quality', 'workshop_quality', 'defenses_quality']
        for metric in quality_metrics:
            value = getattr(self, metric)
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{metric} must be between 0.0 and 1.0, got {value}")
    
    def get_resource_per_capita(self, population: int) -> Dict[str, float]:
        """Calculate per-capita resource availability"""
        if population <= 0:
            return {'food': 1.0, 'materials': 1.0, 'shelter': 1.0, 'tools': 1.0}
        
        return {
            'food': min(2.0, self.food_stores / (population * 3.0)),  # 3 food per person per day
            'materials': min(2.0, self.material_stores / population),
            'shelter': min(1.0, self.shelter_capacity / population),
            'tools': min(1.0, self.tool_count / population)
        }
    
    def consume_daily_resources(self, population: int) -> Dict[str, float]:
        """Consume daily resources based on population"""
        if population <= 0:
            return {'food_consumed': 0, 'spoilage': 0}
        
        # Daily consumption
        daily_food_consumption = population * 2.5  # Base consumption
        
        # Spoilage based on storage quality
        spoilage_rate = 0.02 * (1.0 - self.food_storage_quality)
        daily_spoilage = self.food_stores * spoilage_rate
        
        # Apply consumption and spoilage
        total_food_lost = daily_food_consumption + daily_spoilage
        self.food_stores = max(0.0, self.food_stores - total_food_lost)
        
        # Add natural generation
        self.food_stores += self.natural_food_generation
        self.material_stores += self.natural_material_generation
        
        return {
            'food_consumed': daily_food_consumption,
            'spoilage': daily_spoilage,
            'natural_generation': self.natural_food_generation + self.natural_material_generation
        }


@dataclass
class Governance:
    """Settlement governance and leadership state"""
    
    # Leadership
    current_leader: Optional[str] = None  # NPC ID
    leadership_type: str = "none"         # "elected", "appointed", "dictator", "council", "anarchy"
    leadership_stability: float = 0.5     # How stable the current system is
    leadership_satisfaction: float = 0.5  # How satisfied people are with leadership
    
    # Active governance
    active_proposals: List[Dict[str, Any]] = field(default_factory=list)
    voting_in_progress: bool = False
    last_election_day: Optional[int] = None
    
    # Laws and rules
    established_rules: List[Dict[str, Any]] = field(default_factory=list)
    rule_enforcement_level: float = 0.5   # How well rules are enforced
    
    # Council (if applicable)
    council_members: List[str] = field(default_factory=list)  # NPC IDs
    
    def __post_init__(self):
        """Validate governance values"""
        numeric_fields = ['leadership_stability', 'leadership_satisfaction', 'rule_enforcement_level']
        for field_name in numeric_fields:
            value = getattr(self, field_name)
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{field_name} must be between 0.0 and 1.0, got {value}")
    
    def add_proposal(self, proposal_id: str, proposer: str, proposal_type: str, 
                    description: str, voting_deadline: int):
        """Add a new proposal for voting"""
        proposal = {
            'id': proposal_id,
            'proposer': proposer,
            'type': proposal_type,  # 'rule', 'leadership_change', 'resource_allocation', etc.
            'description': description,
            'voting_deadline': voting_deadline,
            'votes_for': 0,
            'votes_against': 0,
            'abstentions': 0,
            'voters': set()  # Track who has voted
        }
        self.active_proposals.append(proposal)
    
    def cast_vote(self, proposal_id: str, voter_id: str, vote: str) -> bool:
        """Cast a vote on a proposal"""
        proposal = self.get_proposal(proposal_id)
        if not proposal or voter_id in proposal['voters']:
            return False
        
        proposal['voters'].add(voter_id)
        
        if vote == 'for':
            proposal['votes_for'] += 1
        elif vote == 'against':
            proposal['votes_against'] += 1
        else:
            proposal['abstentions'] += 1
        
        return True
    
    def get_proposal(self, proposal_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific proposal"""
        for proposal in self.active_proposals:
            if proposal['id'] == proposal_id:
                return proposal
        return None
    
    def resolve_proposals(self, current_day: int, population: int) -> List[Dict[str, Any]]:
        """Resolve proposals that have reached their deadline"""
        resolved = []
        remaining_proposals = []
        
        for proposal in self.active_proposals:
            if current_day >= proposal['voting_deadline']:
                # Resolve the proposal
                total_votes = proposal['votes_for'] + proposal['votes_against']
                if total_votes > 0:
                    approval_rate = proposal['votes_for'] / total_votes
                    # Need majority to pass
                    passed = approval_rate > 0.5 and proposal['votes_for'] >= population * 0.3
                else:
                    passed = False
                
                proposal['passed'] = passed
                proposal['approval_rate'] = approval_rate if total_votes > 0 else 0
                resolved.append(proposal)
            else:
                remaining_proposals.append(proposal)
        
        self.active_proposals = remaining_proposals
        return resolved
    
    def get_governance_summary(self) -> Dict[str, Any]:
        """Get summary of current governance state"""
        return {
            'leader': self.current_leader,
            'leadership_type': self.leadership_type,
            'stability': self.leadership_stability,
            'satisfaction': self.leadership_satisfaction,
            'active_proposals': len(self.active_proposals),
            'voting_active': self.voting_in_progress,
            'rules_count': len(self.established_rules),
            'enforcement_level': self.rule_enforcement_level,
            'council_size': len(self.council_members)
        }
    
    def _serialize_proposals(self) -> List[Dict[str, Any]]:
        """Convert proposals to serializable format"""
        serialized = []
        for proposal in self.active_proposals:
            prop_copy = proposal.copy()
            # Convert set to list for JSON serialization
            prop_copy['voters'] = list(proposal['voters']) if 'voters' in proposal else []
            serialized.append(prop_copy)
        return serialized
    
    def _deserialize_proposals(self, proposals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert proposals from serialized format"""
        deserialized = []
        for proposal in proposals:
            prop_copy = proposal.copy()
            # Convert list back to set
            prop_copy['voters'] = set(proposal.get('voters', []))
            deserialized.append(prop_copy)
        return deserialized


@dataclass
class Environment:
    """Environmental conditions affecting the settlement"""
    
    # Weather
    current_weather: WeatherType = WeatherType.CLEAR
    weather_severity: float = 0.0          # 0.0 = mild, 1.0 = extreme
    weather_duration_remaining: int = 0    # Days until weather changes
    
    # Threats
    current_threat: ThreatType = ThreatType.NONE
    threat_severity: float = 0.0           # 0.0 = minor, 1.0 = catastrophic
    threat_duration_remaining: int = 0     # Days until threat resolves
    
    # Seasonal factors
    season: str = "spring"                 # "spring", "summer", "fall", "winter"
    days_in_season: int = 0               # Days since season started
    
    def __post_init__(self):
        """Validate environment values"""
        numeric_fields = ['weather_severity', 'threat_severity']
        for field_name in numeric_fields:
            value = getattr(self, field_name)
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{field_name} must be between 0.0 and 1.0, got {value}")
    
    def advance_day(self):
        """Advance environmental conditions by one day"""
        self.days_in_season += 1
        
        # Change seasons every 90 days
        if self.days_in_season >= 90:
            self.days_in_season = 0
            seasons = ["spring", "summer", "fall", "winter"]
            current_index = seasons.index(self.season)
            self.season = seasons[(current_index + 1) % len(seasons)]
        
        # Update weather
        self.weather_duration_remaining = max(0, self.weather_duration_remaining - 1)
        if self.weather_duration_remaining == 0:
            self._generate_new_weather()
        
        # Update threats
        self.threat_duration_remaining = max(0, self.threat_duration_remaining - 1)
        if self.threat_duration_remaining == 0:
            self._generate_new_threat()
    
    def _generate_new_weather(self):
        """Generate new weather conditions"""
        # Weather probabilities by season
        weather_probs = {
            "spring": {WeatherType.CLEAR: 0.5, WeatherType.RAIN: 0.3, WeatherType.STORM: 0.2},
            "summer": {WeatherType.CLEAR: 0.6, WeatherType.EXTREME_HEAT: 0.2, WeatherType.DROUGHT: 0.2},
            "fall": {WeatherType.CLEAR: 0.4, WeatherType.RAIN: 0.4, WeatherType.STORM: 0.2},
            "winter": {WeatherType.CLEAR: 0.3, WeatherType.EXTREME_COLD: 0.4, WeatherType.STORM: 0.3}
        }
        
        season_probs = weather_probs.get(self.season, weather_probs["spring"])
        self.current_weather = random.choices(
            list(season_probs.keys()), 
            weights=list(season_probs.values())
        )[0]
        
        # Set severity and duration
        if self.current_weather == WeatherType.CLEAR:
            self.weather_severity = 0.0
            self.weather_duration_remaining = random.randint(3, 7)
        else:
            self.weather_severity = random.uniform(0.3, 0.8)
            self.weather_duration_remaining = random.randint(1, 4)
    
    def _generate_new_threat(self):
        """Generate new threat conditions"""
        # Base threat probability (most of the time, no threats)
        threat_prob = 0.1
        
        if random.random() < threat_prob:
            threats = [ThreatType.WILDLIFE, ThreatType.RAIDERS, ThreatType.NATURAL_DISASTER, 
                      ThreatType.RESOURCE_DEPLETION, ThreatType.DISEASE]
            self.current_threat = random.choice(threats)
            self.threat_severity = random.uniform(0.2, 0.7)
            self.threat_duration_remaining = random.randint(1, 5)
        else:
            self.current_threat = ThreatType.NONE
            self.threat_severity = 0.0
            self.threat_duration_remaining = 0
    
    def get_environmental_effects(self) -> Dict[str, float]:
        """Get current environmental effects on settlement"""
        effects = {
            'gathering_efficiency': 1.0,
            'construction_efficiency': 1.0,
            'health_impact': 0.0,
            'mood_impact': 0.0,
            'food_spoilage_rate': 1.0
        }
        
        # Weather effects
        if self.current_weather == WeatherType.RAIN:
            effects['gathering_efficiency'] *= (1.0 - self.weather_severity * 0.3)
            effects['construction_efficiency'] *= (1.0 - self.weather_severity * 0.4)
        elif self.current_weather == WeatherType.STORM:
            effects['gathering_efficiency'] *= (1.0 - self.weather_severity * 0.6)
            effects['construction_efficiency'] *= (1.0 - self.weather_severity * 0.7)
            effects['mood_impact'] -= self.weather_severity * 0.2
        elif self.current_weather == WeatherType.EXTREME_COLD:
            effects['gathering_efficiency'] *= (1.0 - self.weather_severity * 0.4)
            effects['health_impact'] -= self.weather_severity * 0.1
            effects['food_spoilage_rate'] *= (1.0 - self.weather_severity * 0.3)  # Cold preserves food
        elif self.current_weather == WeatherType.EXTREME_HEAT:
            effects['health_impact'] -= self.weather_severity * 0.1
            effects['food_spoilage_rate'] *= (1.0 + self.weather_severity * 0.5)  # Heat spoils food
        elif self.current_weather == WeatherType.DROUGHT:
            effects['gathering_efficiency'] *= (1.0 - self.weather_severity * 0.5)
        
        # Threat effects
        if self.current_threat != ThreatType.NONE:
            effects['mood_impact'] -= self.threat_severity * 0.3
            
            if self.current_threat == ThreatType.WILDLIFE:
                effects['gathering_efficiency'] *= (1.0 - self.threat_severity * 0.2)
            elif self.current_threat == ThreatType.RAIDERS:
                effects['gathering_efficiency'] *= (1.0 - self.threat_severity * 0.4)
                effects['mood_impact'] -= self.threat_severity * 0.2
            elif self.current_threat == ThreatType.DISEASE:
                effects['health_impact'] -= self.threat_severity * 0.3
        
        return effects


@dataclass
class SocialClimate:
    """Overall social dynamics and mood of the settlement"""
    
    # Community metrics (0.0 - 1.0)
    overall_mood: float = 0.5
    cooperation_level: float = 0.5
    conflict_level: float = 0.3
    trust_network_density: float = 0.4
    
    # Social events and trends
    recent_events: List[Dict[str, Any]] = field(default_factory=list)
    mood_trend: float = 0.0  # -1.0 = declining, 0.0 = stable, 1.0 = improving
    
    def __post_init__(self):
        """Validate social climate values"""
        numeric_fields = ['overall_mood', 'cooperation_level', 'conflict_level', 'trust_network_density']
        for field_name in numeric_fields:
            value = getattr(self, field_name)
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{field_name} must be between 0.0 and 1.0, got {value}")
    
    def add_social_event(self, event_type: str, impact: float, description: str, 
                        participants: List[str] = None):
        """Add a social event that affects community mood"""
        event = {
            'type': event_type,
            'impact': impact,
            'description': description,
            'participants': participants or [],
            'timestamp': datetime.now().isoformat()
        }
        
        self.recent_events.append(event)
        
        # Keep only recent events (last 50)
        if len(self.recent_events) > 50:
            self.recent_events = self.recent_events[-50:]
        
        # Apply immediate impact
        self.overall_mood = max(0.0, min(1.0, self.overall_mood + impact))
        
        # Update cooperation/conflict based on event type
        if event_type in ['help', 'alliance_formed', 'resource_sharing']:
            self.cooperation_level = min(1.0, self.cooperation_level + abs(impact) * 0.5)
        elif event_type in ['betrayal', 'conflict', 'resource_theft']:
            self.conflict_level = min(1.0, self.conflict_level + abs(impact) * 0.5)
            self.cooperation_level = max(0.0, self.cooperation_level - abs(impact) * 0.3)
    
    def calculate_daily_mood_change(self, population: int, governance: Governance, 
                                  environment: Environment) -> float:
        """Calculate how mood should change based on current conditions"""
        base_change = 0.0
        
        # Governance effects
        if governance.current_leader:
            leadership_effect = (governance.leadership_satisfaction - 0.5) * 0.02
            base_change += leadership_effect
        else:
            # No leadership causes gradual mood decline
            base_change -= 0.01
        
        # Environmental effects
        env_effects = environment.get_environmental_effects()
        base_change += env_effects['mood_impact']
        
        # Population effects (overcrowding, loneliness)
        if population > 30:  # Overcrowding
            base_change -= (population - 30) * 0.001
        elif population < 5:  # Too few people
            base_change -= (5 - population) * 0.002
        
        # Apply change
        old_mood = self.overall_mood
        self.overall_mood = max(0.0, min(1.0, self.overall_mood + base_change))
        
        # Update trend
        actual_change = self.overall_mood - old_mood
        self.mood_trend = max(-1.0, min(1.0, self.mood_trend * 0.8 + actual_change * 20))
        
        return actual_change
    
    def get_social_climate_summary(self) -> Dict[str, Any]:
        """Get summary of current social climate"""
        recent_event_count = len([e for e in self.recent_events 
                                if (datetime.now() - datetime.fromisoformat(e['timestamp'])).days < 7])
        
        return {
            'overall_mood': self.overall_mood,
            'cooperation_level': self.cooperation_level,
            'conflict_level': self.conflict_level,
            'trust_network_density': self.trust_network_density,
            'mood_trend': self.mood_trend,
            'recent_events_week': recent_event_count,
            'mood_description': self._get_mood_description()
        }
    
    def _get_mood_description(self) -> str:
        """Get human-readable mood description"""
        if self.overall_mood >= 0.8:
            return "jubilant"
        elif self.overall_mood >= 0.6:
            return "content"
        elif self.overall_mood >= 0.4:
            return "neutral"
        elif self.overall_mood >= 0.2:
            return "troubled"
        else:
            return "despairing"


@dataclass
class WorldState:
    """Complete world state encompassing all settlement systems"""
    
    # Core systems
    settlement: Settlement = field(default_factory=Settlement)
    governance: Governance = field(default_factory=Governance)
    environment: Environment = field(default_factory=Environment)
    social_climate: SocialClimate = field(default_factory=SocialClimate)
    
    # Time tracking
    current_day: int = 1
    current_season: str = "spring"
    
    # Population tracking
    population: int = 25  # Total NPCs
    active_npcs: List[str] = field(default_factory=list)  # NPC IDs
    
    def __post_init__(self):
        """Initialize world state"""
        if self.population < 0:
            raise ValueError("Population cannot be negative")
    
    def advance_day(self) -> Dict[str, Any]:
        """Advance the world by one day and return summary of changes"""
        self.current_day += 1
        
        # Advance environmental conditions
        self.environment.advance_day()
        
        # Process daily resource consumption
        consumption_data = self.settlement.consume_daily_resources(self.population)
        
        # Update social climate
        mood_change = self.social_climate.calculate_daily_mood_change(
            self.population, self.governance, self.environment
        )
        
        # Resolve any proposals
        resolved_proposals = self.governance.resolve_proposals(self.current_day, self.population)
        
        # Calculate environmental effects
        env_effects = self.environment.get_environmental_effects()
        
        return {
            'day': self.current_day,
            'consumption': consumption_data,
            'mood_change': mood_change,
            'resolved_proposals': resolved_proposals,
            'environmental_effects': env_effects,
            'weather': self.environment.current_weather.value,
            'threats': self.environment.current_threat.value
        }
    
    def add_npc(self, npc_id: str):
        """Add an NPC to the world"""
        if npc_id not in self.active_npcs:
            self.active_npcs.append(npc_id)
            self.population = len(self.active_npcs)
    
    def remove_npc(self, npc_id: str):
        """Remove an NPC from the world"""
        if npc_id in self.active_npcs:
            self.active_npcs.remove(npc_id)
            self.population = len(self.active_npcs)
    
    def process_action_outcome(self, npc_id: str, action: ActionType, success: bool, 
                             outcome_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process the world-level effects of an NPC action"""
        outcome_data = outcome_data or {}
        world_changes = {}
        
        # Resource actions
        if action == ActionType.GATHER_FOOD and success:
            amount = outcome_data.get('amount_gathered', 3.0)
            env_effects = self.environment.get_environmental_effects()
            actual_amount = amount * env_effects['gathering_efficiency']
            
            self.settlement.food_stores += actual_amount
            world_changes['food_gained'] = actual_amount
        
        elif action == ActionType.GATHER_MATERIALS and success:
            amount = outcome_data.get('amount_gathered', 2.0)
            env_effects = self.environment.get_environmental_effects()
            actual_amount = amount * env_effects['gathering_efficiency']
            
            self.settlement.material_stores += actual_amount
            world_changes['materials_gained'] = actual_amount
        
        elif action == ActionType.BUILD_SHELTER and success:
            materials_used = outcome_data.get('materials_used', 5.0)
            if self.settlement.material_stores >= materials_used:
                self.settlement.material_stores -= materials_used
                self.settlement.shelter_capacity += 2
                world_changes['shelter_added'] = 2
        
        elif action == ActionType.CRAFT_TOOLS and success:
            materials_used = outcome_data.get('materials_used', 3.0)
            if self.settlement.material_stores >= materials_used:
                self.settlement.material_stores -= materials_used
                self.settlement.tool_count += 1
                world_changes['tools_created'] = 1
        
        # Social actions
        elif action in [ActionType.HELP_RANDOM_NPC, ActionType.SHARE_RESOURCES] and success:
            self.social_climate.add_social_event(
                'cooperation', 0.02, 
                f"{npc_id} helped another community member",
                [npc_id]
            )
            world_changes['social_impact'] = 'positive'
        
        elif action == ActionType.FORM_ALLIANCE and success:
            self.social_climate.add_social_event(
                'alliance_formed', 0.03,
                f"{npc_id} formed a new alliance",
                [npc_id]
            )
            world_changes['social_impact'] = 'alliance_formed'
        
        # Governance actions
        elif action == ActionType.PROPOSE_NEW_RULE and success:
            proposal_id = f"proposal_{self.current_day}_{npc_id}"
            self.governance.add_proposal(
                proposal_id, npc_id, 'rule',
                outcome_data.get('proposal_description', 'New community rule'),
                self.current_day + 3  # 3 days to vote
            )
            world_changes['proposal_added'] = proposal_id
        
        elif action == ActionType.CHALLENGE_LEADERSHIP and success:
            if self.governance.current_leader != npc_id:
                # Leadership challenge affects stability
                self.governance.leadership_stability *= 0.8
                self.social_climate.add_social_event(
                    'leadership_challenge', -0.05,
                    f"{npc_id} challenged the current leadership",
                    [npc_id, self.governance.current_leader]
                )
                world_changes['leadership_challenged'] = True
        
        return world_changes
    
    def get_world_summary(self) -> Dict[str, Any]:
        """Get comprehensive world state summary"""
        resource_per_capita = self.settlement.get_resource_per_capita(self.population)
        
        return {
            'basic_info': {
                'day': self.current_day,
                'population': self.population,
                'season': self.environment.season
            },
            'resources': {
                'food_stores': self.settlement.food_stores,
                'material_stores': self.settlement.material_stores,
                'tools': self.settlement.tool_count,
                'shelter_capacity': self.settlement.shelter_capacity,
                'per_capita': resource_per_capita
            },
            'environment': {
                'weather': self.environment.current_weather.value,
                'weather_severity': self.environment.weather_severity,
                'threat': self.environment.current_threat.value,
                'threat_severity': self.environment.threat_severity,
                'environmental_effects': self.environment.get_environmental_effects()
            },
            'social': self.social_climate.get_social_climate_summary(),
            'governance': self.governance.get_governance_summary(),
            'urgent_issues': self._identify_urgent_issues()
        }
    
    def _identify_urgent_issues(self) -> List[str]:
        """Identify urgent issues requiring attention"""
        issues = []
        
        # Resource shortages
        per_capita = self.settlement.get_resource_per_capita(self.population)
        if per_capita['food'] < 0.3:
            issues.append("food_shortage")
        if per_capita['shelter'] < 0.8:
            issues.append("shelter_shortage")
        
        # Environmental threats
        if self.environment.threat_severity > 0.6:
            issues.append(f"severe_{self.environment.current_threat.value}")
        
        # Social problems
        if self.social_climate.overall_mood < 0.3:
            issues.append("low_morale")
        if self.social_climate.conflict_level > 0.7:
            issues.append("high_conflict")
        
        # Governance problems
        if not self.governance.current_leader and self.social_climate.conflict_level > 0.5:
            issues.append("leadership_crisis")
        
        return issues
    
    def get_npc_world_context(self, npc_id: str) -> Dict[str, Any]:
        """Get world context relevant for NPC decision making"""
        per_capita = self.settlement.get_resource_per_capita(self.population)
        env_effects = self.environment.get_environmental_effects()
        
        return {
            # Resource availability
            'settlement_resources': per_capita,
            'raw_resources': {
                'food_stores': self.settlement.food_stores,
                'material_stores': self.settlement.material_stores
            },
            
            # Social context
            'settlement_mood': self.social_climate.overall_mood,
            'cooperation_level': self.social_climate.cooperation_level,
            'conflict_level': self.social_climate.conflict_level,
            'trust_network_density': self.social_climate.trust_network_density,
            
            # Governance context
            'has_leader': self.governance.current_leader is not None,
            'is_leader': self.governance.current_leader == npc_id,
            'leadership_stability': self.governance.leadership_stability,
            'active_proposals': len(self.governance.active_proposals),
            'voting_in_progress': self.governance.voting_in_progress,
            
            # Environmental context
            'weather_severity': self.environment.weather_severity,
            'threat_level': self.environment.threat_severity,
            'external_threats': self.environment.current_threat.value,
            'environmental_effects': env_effects,
            
            # Urgency indicators
            'urgent_issues': self._identify_urgent_issues(),
            'population': self.population
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'settlement': {
                'food_stores': self.settlement.food_stores,
                'material_stores': self.settlement.material_stores,
                'tool_count': self.settlement.tool_count,
                'shelter_capacity': self.settlement.shelter_capacity,
                'shelter_quality': self.settlement.shelter_quality,
                'food_storage_quality': self.settlement.food_storage_quality,
                'workshop_quality': self.settlement.workshop_quality,
                'defenses_quality': self.settlement.defenses_quality
            },
            'governance': {
                'current_leader': self.governance.current_leader,
                'leadership_type': self.governance.leadership_type,
                'leadership_stability': self.governance.leadership_stability,
                'leadership_satisfaction': self.governance.leadership_satisfaction,
                'active_proposals': self.governance._serialize_proposals(),  # Use serialization method
                'established_rules': self.governance.established_rules,
                'council_members': self.governance.council_members
            },
            'environment': {
                'current_weather': self.environment.current_weather.value,
                'weather_severity': self.environment.weather_severity,
                'weather_duration_remaining': self.environment.weather_duration_remaining,
                'current_threat': self.environment.current_threat.value,
                'threat_severity': self.environment.threat_severity,
                'threat_duration_remaining': self.environment.threat_duration_remaining,
                'season': self.environment.season,
                'days_in_season': self.environment.days_in_season
            },
            'social_climate': {
                'overall_mood': self.social_climate.overall_mood,
                'cooperation_level': self.social_climate.cooperation_level,
                'conflict_level': self.social_climate.conflict_level,
                'trust_network_density': self.social_climate.trust_network_density,
                'recent_events': self.social_climate.recent_events,
                'mood_trend': self.social_climate.mood_trend
            },
            'meta': {
                'current_day': self.current_day,
                'population': self.population,
                'active_npcs': self.active_npcs
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorldState':
        """Create from dictionary"""
        world = cls()
        
        # Reconstruct settlement
        settlement_data = data.get('settlement', {})
        world.settlement = Settlement(
            food_stores=settlement_data.get('food_stores', 100.0),
            material_stores=settlement_data.get('material_stores', 50.0),
            tool_count=settlement_data.get('tool_count', 10),
            shelter_capacity=settlement_data.get('shelter_capacity', 30),
            shelter_quality=settlement_data.get('shelter_quality', 0.6),
            food_storage_quality=settlement_data.get('food_storage_quality', 0.5),
            workshop_quality=settlement_data.get('workshop_quality', 0.4),
            defenses_quality=settlement_data.get('defenses_quality', 0.3)
        )
        
        # Reconstruct governance
        gov_data = data.get('governance', {})
        world.governance = Governance(
            current_leader=gov_data.get('current_leader'),
            leadership_type=gov_data.get('leadership_type', 'none'),
            leadership_stability=gov_data.get('leadership_stability', 0.5),
            leadership_satisfaction=gov_data.get('leadership_satisfaction', 0.5),
            active_proposals=[],  # Will be deserialized separately
            established_rules=gov_data.get('established_rules', []),
            council_members=gov_data.get('council_members', [])
        )
        
        # Deserialize proposals properly
        if 'active_proposals' in gov_data:
            world.governance.active_proposals = world.governance._deserialize_proposals(
                gov_data['active_proposals']
            )
        
        # Reconstruct environment
        env_data = data.get('environment', {})
        world.environment = Environment(
            current_weather=WeatherType(env_data.get('current_weather', 'clear')),
            weather_severity=env_data.get('weather_severity', 0.0),
            weather_duration_remaining=env_data.get('weather_duration_remaining', 0),
            current_threat=ThreatType(env_data.get('current_threat', 'none')),
            threat_severity=env_data.get('threat_severity', 0.0),
            threat_duration_remaining=env_data.get('threat_duration_remaining', 0),
            season=env_data.get('season', 'spring'),
            days_in_season=env_data.get('days_in_season', 0)
        )
        
        # Reconstruct social climate
        social_data = data.get('social_climate', {})
        world.social_climate = SocialClimate(
            overall_mood=social_data.get('overall_mood', 0.5),
            cooperation_level=social_data.get('cooperation_level', 0.5),
            conflict_level=social_data.get('conflict_level', 0.3),
            trust_network_density=social_data.get('trust_network_density', 0.4),
            recent_events=social_data.get('recent_events', []),
            mood_trend=social_data.get('mood_trend', 0.0)
        )
        
        # Reconstruct meta information
        meta_data = data.get('meta', {})
        world.current_day = meta_data.get('current_day', 1)
        world.population = meta_data.get('population', 25)
        world.active_npcs = meta_data.get('active_npcs', [])
        
        return world
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'WorldState':
        """Create from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)