rl_game_server/
│
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration management
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py           # API endpoint definitions
│   │   ├── models.py           # Pydantic models for requests/responses
│   │   └── dependencies.py     # Shared dependencies for routes
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── state_manager.py    # Game state representation and translation
│   │   ├── action_space.py     # Action definitions and mappings
│   │   └── reward_calculator.py # Reward function implementations
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py       # Abstract base class for all agents
│   │   ├── q_learning_agent.py # Q-learning implementation
│   │   ├── dqn_agent.py        # Deep Q-Network (for future use)
│   │   └── agent_factory.py    # Factory pattern for creating agents
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── model_manager.py    # Model loading, saving, versioning
│   │   └── model_registry.py   # Track available models and their metadata
│   │
│   └── utils/
│       ├── __init__.py
│       ├── logging.py          # Structured logging setup
│       └── metrics.py          # Performance tracking
│
├── training/
│   ├── __init__.py
│   ├── train_survival.py       # Script to train survival game agents
│   ├── environments/
│   │   ├── __init__.py
│   │   └── survival_env.py     # Training environment matching your game
│   └── configs/
│       └── survival_config.yaml # Training hyperparameters
│
├── models/
│   └── pretrained/
│       └── survival_v1.pkl     # Your first pretrained model will go here
│
├── tests/
│   ├── __init__.py
│   ├── test_api.py
│   ├── test_agents.py
│   └── test_state_manager.py
│
├── scripts/
│   ├── test_server.py          # Simple script to test API calls
│   └── benchmark.py            # Performance testing
│
├── requirements.txt
├── README.md
├── .env.example                # Example environment variables
└── docker-compose.yml          # For easy deployment later