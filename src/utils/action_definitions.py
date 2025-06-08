from enum import Enum
from typing import Dict, Any, List

class ActionType(Enum):
    """All possible actions NPCs can take"""
    
    # Resource Actions
    GATHER_FOOD = "gather_food"
    GATHER_MATERIALS = "gather_materials"
    CRAFT_TOOLS = "craft_tools"
    BUILD_SHELTER = "build_shelter"
    
    # Social Actions
    HELP_RANDOM_NPC = "help_random_npc"
    SHARE_RESOURCES = "share_resources"
    START_CONVERSATION = "start_conversation"
    FORM_ALLIANCE = "form_alliance"
    
    # Governance Actions
    VOTE_ON_PROPOSAL = "vote_on_proposal"
    PROPOSE_NEW_RULE = "propose_new_rule"
    CHALLENGE_LEADERSHIP = "challenge_leadership"
    SUPPORT_LEADER = "support_leader"
    
    # Personal Actions
    REST = "rest"
    PRACTICE_SKILLS = "practice_skills"
    OBSERVE_OTHERS = "observe_others"
    DO_NOTHING = "do_nothing"


# Action metadata for game mechanics
ACTION_METADATA = {
    ActionType.GATHER_FOOD: {
        'energy_cost': 0.3,
        'base_success_rate': 0.7,
        'category': 'resource'
    },
    ActionType.GATHER_MATERIALS: {
        'energy_cost': 0.4,
        'base_success_rate': 0.8,
        'category': 'resource'
    },
    ActionType.CRAFT_TOOLS: {
        'energy_cost': 0.2,
        'base_success_rate': 0.6,
        'category': 'resource'
    },
    ActionType.BUILD_SHELTER: {
        'energy_cost': 0.5,
        'base_success_rate': 0.5,
        'category': 'resource'
    },
    ActionType.HELP_RANDOM_NPC: {
        'energy_cost': 0.2,
        'base_success_rate': 0.8,
        'category': 'social'
    },
    ActionType.SHARE_RESOURCES: {
        'energy_cost': 0.1,
        'base_success_rate': 0.9,
        'category': 'social'
    },
    ActionType.START_CONVERSATION: {
        'energy_cost': 0.1,
        'base_success_rate': 0.7,
        'category': 'social'
    },
    ActionType.FORM_ALLIANCE: {
        'energy_cost': 0.1,
        'base_success_rate': 0.4,
        'category': 'social'
    },
    ActionType.VOTE_ON_PROPOSAL: {
        'energy_cost': 0.05,
        'base_success_rate': 0.9,
        'category': 'governance'
    },
    ActionType.PROPOSE_NEW_RULE: {
        'energy_cost': 0.15,
        'base_success_rate': 0.3,
        'category': 'governance'
    },
    ActionType.CHALLENGE_LEADERSHIP: {
        'energy_cost': 0.3,
        'base_success_rate': 0.2,
        'category': 'governance'
    },
    ActionType.SUPPORT_LEADER: {
        'energy_cost': 0.1,
        'base_success_rate': 0.8,
        'category': 'governance'
    },
    ActionType.REST: {
        'energy_cost': -0.4,  # Negative = restores energy
        'base_success_rate': 0.95,
        'category': 'personal'
    },
    ActionType.PRACTICE_SKILLS: {
        'energy_cost': 0.2,
        'base_success_rate': 0.9,
        'category': 'personal'
    },
    ActionType.OBSERVE_OTHERS: {
        'energy_cost': 0.05,
        'base_success_rate': 0.8,
        'category': 'personal'
    },
    ActionType.DO_NOTHING: {
        'energy_cost': 0.0,
        'base_success_rate': 1.0,
        'category': 'personal'
    }
}


def get_action_metadata(action: ActionType) -> Dict[str, Any]:
    """Get metadata for an action"""
    return ACTION_METADATA.get(action, {
        'energy_cost': 0.1,
        'base_success_rate': 0.5,
        'category': 'unknown'
    })


def get_actions_by_category(category: str) -> List[ActionType]:
    """Get all actions in a category"""
    return [action for action, metadata in ACTION_METADATA.items() 
            if metadata['category'] == category]