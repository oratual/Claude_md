#!/usr/bin/env python3
"""
Examples of creating custom agents for Batman Incorporated
"""

from typing import List, Dict, Any
from abc import abstractmethod

from src.agents.base import BaseAgent
from src.core.task import Task, TaskType
from src.features.chapter_logger import ChapterLogger


class DataScientistAgent(BaseAgent):
    """Custom agent specializing in data science and machine learning"""
    
    def __init__(self, logger: ChapterLogger = None):
        super().__init__(
            name="DataScientist",
            role="ML Engineer & Data Analyst",
            logger=logger
        )
    
    def get_system_prompt(self) -> str:
        return """You are a Data Scientist agent specializing in machine learning,
data analysis, and statistical modeling. Your expertise includes:

- Machine learning algorithms and frameworks (scikit-learn, TensorFlow, PyTorch)
- Data preprocessing and feature engineering
- Statistical analysis and hypothesis testing
- Data visualization (matplotlib, seaborn, plotly)
- Big data tools (Spark, Hadoop)
- SQL and NoSQL databases
- A/B testing and experimentation

You write clean, well-documented code with proper model evaluation and validation.
You always consider data quality, bias, and ethical implications in your work."""
    
    def get_specialties(self) -> List[str]:
        return [
            "machine learning",
            "data analysis",
            "statistics",
            "data visualization",
            "feature engineering",
            "model deployment",
            "A/B testing",
            "ETL pipelines"
        ]


class MobileAgent(BaseAgent):
    """Custom agent specializing in mobile app development"""
    
    def __init__(self, logger: ChapterLogger = None):
        super().__init__(
            name="MobileDev",
            role="Mobile Application Developer",
            logger=logger
        )
    
    def get_system_prompt(self) -> str:
        return """You are a Mobile Developer agent specializing in iOS and Android
application development. Your expertise includes:

- Native iOS development (Swift, SwiftUI, UIKit)
- Native Android development (Kotlin, Jetpack Compose)
- Cross-platform frameworks (React Native, Flutter)
- Mobile UI/UX best practices
- App performance optimization
- Push notifications and background services
- App store deployment and guidelines
- Mobile security best practices

You create responsive, performant mobile applications with great user experience."""
    
    def get_specialties(self) -> List[str]:
        return [
            "iOS development",
            "Android development",
            "React Native",
            "Flutter",
            "mobile UI/UX",
            "app optimization",
            "mobile testing",
            "app deployment"
        ]


class BlockchainAgent(BaseAgent):
    """Custom agent specializing in blockchain and Web3 development"""
    
    def __init__(self, logger: ChapterLogger = None):
        super().__init__(
            name="BlockchainDev",
            role="Blockchain & Smart Contract Developer",
            logger=logger
        )
    
    def get_system_prompt(self) -> str:
        return """You are a Blockchain Developer agent specializing in distributed
ledger technology and smart contract development. Your expertise includes:

- Smart contract development (Solidity, Rust)
- Blockchain platforms (Ethereum, Polygon, Solana)
- Web3 integration (ethers.js, web3.js)
- DeFi protocols and patterns
- NFT standards and implementations
- Security auditing and best practices
- Gas optimization techniques
- Decentralized storage (IPFS, Arweave)

You prioritize security, efficiency, and decentralization in your implementations."""
    
    def get_specialties(self) -> List[str]:
        return [
            "smart contracts",
            "Solidity",
            "Web3",
            "DeFi",
            "NFTs",
            "blockchain security",
            "gas optimization",
            "dApp development"
        ]


class GameDevAgent(BaseAgent):
    """Custom agent specializing in game development"""
    
    def __init__(self, logger: ChapterLogger = None):
        super().__init__(
            name="GameDev",
            role="Game Developer & Designer",
            logger=logger
        )
    
    def get_system_prompt(self) -> str:
        return """You are a Game Developer agent specializing in game development
and design. Your expertise includes:

- Game engines (Unity, Unreal Engine, Godot)
- Game programming patterns and architecture
- Physics and mathematics for games
- AI for games (pathfinding, behavior trees)
- Graphics programming and shaders
- Multiplayer networking
- Game design and balancing
- Performance optimization for games

You create engaging, well-optimized games with clean architecture."""
    
    def get_specialties(self) -> List[str]:
        return [
            "Unity",
            "Unreal Engine",
            "game design",
            "game AI",
            "graphics programming",
            "multiplayer",
            "game optimization",
            "level design"
        ]


class CloudArchitectAgent(BaseAgent):
    """Custom agent specializing in cloud architecture and infrastructure"""
    
    def __init__(self, logger: ChapterLogger = None):
        super().__init__(
            name="CloudArchitect",
            role="Cloud Solutions Architect",
            logger=logger
        )
    
    def get_system_prompt(self) -> str:
        return """You are a Cloud Architect agent specializing in designing and
implementing scalable cloud solutions. Your expertise includes:

- AWS services and architecture patterns
- Azure and GCP platforms
- Infrastructure as Code (Terraform, CloudFormation)
- Kubernetes and container orchestration
- Microservices architecture
- Serverless computing
- Cloud security and compliance
- Cost optimization strategies
- High availability and disaster recovery

You design resilient, scalable, and cost-effective cloud solutions."""
    
    def get_specialties(self) -> List[str]:
        return [
            "AWS",
            "Azure",
            "Kubernetes",
            "Terraform",
            "microservices",
            "serverless",
            "cloud security",
            "DevOps"
        ]


class CustomAgentRegistry:
    """Registry for managing custom agents"""
    
    def __init__(self):
        self.agents: Dict[str, type] = {}
        self._register_default_custom_agents()
    
    def _register_default_custom_agents(self):
        """Register the default custom agents"""
        self.register("data_scientist", DataScientistAgent)
        self.register("mobile", MobileAgent)
        self.register("blockchain", BlockchainAgent)
        self.register("gamedev", GameDevAgent)
        self.register("cloud_architect", CloudArchitectAgent)
    
    def register(self, name: str, agent_class: type):
        """Register a custom agent"""
        if not issubclass(agent_class, BaseAgent):
            raise ValueError(f"{agent_class} must inherit from BaseAgent")
        self.agents[name] = agent_class
    
    def create_agent(self, name: str, logger: ChapterLogger = None) -> BaseAgent:
        """Create an instance of a registered agent"""
        if name not in self.agents:
            raise ValueError(f"Unknown agent: {name}")
        return self.agents[name](logger=logger)
    
    def list_agents(self) -> List[str]:
        """List all registered custom agents"""
        return list(self.agents.keys())


def example_custom_agent_usage():
    """Example of using custom agents"""
    print("=== Custom Agent Usage Example ===\n")
    
    logger = ChapterLogger("Custom Agent Demo")
    registry = CustomAgentRegistry()
    
    # Create a data science task
    ml_task = Task(
        id="ml-001",
        title="Build recommendation system",
        description="Create a movie recommendation system using collaborative filtering",
        type=TaskType.DEVELOPMENT,
        command="Build a movie recommendation system with user-item collaborative filtering"
    )
    
    # Use data scientist agent
    logger.start_chapter("Machine Learning", "Build recommendation system")
    data_scientist = registry.create_agent("data_scientist", logger)
    
    print("Executing task with Data Scientist agent...")
    success = data_scientist.execute_task(ml_task)
    
    if success:
        print("✓ Recommendation system implemented!")
    
    logger.end_chapter("ML task completed")
    
    # Create a mobile task
    mobile_task = Task(
        id="mobile-001",
        title="Create mobile app",
        description="Build a cross-platform mobile app for the recommendation system",
        type=TaskType.DEVELOPMENT,
        command="Create a React Native app that consumes the recommendation API"
    )
    
    # Use mobile agent
    logger.start_chapter("Mobile Development", "Build mobile app")
    mobile_dev = registry.create_agent("mobile", logger)
    
    print("\nExecuting task with Mobile Developer agent...")
    success = mobile_dev.execute_task(mobile_task)
    
    if success:
        print("✓ Mobile app created!")
    
    logger.end_chapter("Mobile task completed")
    
    # Show all available custom agents
    print("\nAvailable custom agents:")
    for agent_name in registry.list_agents():
        agent = registry.create_agent(agent_name)
        print(f"- {agent_name}: {agent.role}")
        print(f"  Specialties: {', '.join(agent.get_specialties()[:3])}...")


def example_extending_batman():
    """Example of extending Batman with custom agents"""
    print("\n=== Extending Batman with Custom Agents ===\n")
    
    from src.core.batman import BatmanIncorporated
    from src.core.config import Config
    
    # Custom Batman class that includes new agents
    class ExtendedBatman(BatmanIncorporated):
        def __init__(self, config: Config, verbose: bool = False):
            super().__init__(config, verbose)
            self.custom_registry = CustomAgentRegistry()
        
        def _select_agent_for_task(self, task_description: str) -> str:
            """Extended agent selection including custom agents"""
            desc_lower = task_description.lower()
            
            # Check for custom agent keywords
            if any(word in desc_lower for word in ["ml", "machine learning", "data science", "recommendation"]):
                return "data_scientist"
            elif any(word in desc_lower for word in ["mobile", "ios", "android", "react native"]):
                return "mobile"
            elif any(word in desc_lower for word in ["blockchain", "smart contract", "web3", "defi"]):
                return "blockchain"
            elif any(word in desc_lower for word in ["game", "unity", "unreal"]):
                return "gamedev"
            elif any(word in desc_lower for word in ["cloud", "aws", "kubernetes", "terraform"]):
                return "cloud_architect"
            
            # Fall back to original agent selection
            return super()._select_agent_for_task(task_description)
    
    # Use extended Batman
    config = Config()
    extended_batman = ExtendedBatman(config, verbose=True)
    
    # Execute tasks that will use custom agents
    tasks = [
        "Build a machine learning model to predict user churn",
        "Create a mobile app for cryptocurrency portfolio tracking",
        "Deploy the application to AWS with auto-scaling",
        "Implement a smart contract for decentralized voting",
        "Build a multiplayer game with Unity"
    ]
    
    for task in tasks:
        print(f"\nTask: {task}")
        agent = extended_batman._select_agent_for_task(task)
        print(f"Selected agent: {agent}")


def example_agent_collaboration():
    """Example of custom agents collaborating"""
    print("\n=== Custom Agent Collaboration ===\n")
    
    logger = ChapterLogger("Agent Collaboration")
    registry = CustomAgentRegistry()
    
    # Scenario: Build a blockchain game with mobile app
    
    # Step 1: Smart contract development
    logger.start_chapter("Blockchain Development", "Create game smart contracts")
    blockchain_agent = registry.create_agent("blockchain", logger)
    
    contract_task = Task(
        id="blockchain-001",
        title="Create NFT game contracts",
        description="Develop smart contracts for NFT-based game items",
        type=TaskType.DEVELOPMENT
    )
    
    blockchain_agent.execute_task(contract_task)
    logger.end_chapter("Smart contracts deployed")
    
    # Step 2: Game development
    logger.start_chapter("Game Development", "Build the game")
    game_agent = registry.create_agent("gamedev", logger)
    
    game_task = Task(
        id="game-001",
        title="Create blockchain game",
        description="Build a game that integrates with the smart contracts",
        type=TaskType.DEVELOPMENT
    )
    
    game_agent.execute_task(game_task)
    logger.end_chapter("Game created")
    
    # Step 3: Mobile app
    logger.start_chapter("Mobile App", "Create companion mobile app")
    mobile_agent = registry.create_agent("mobile", logger)
    
    app_task = Task(
        id="mobile-001",
        title="Build game companion app",
        description="Create mobile app for managing game NFTs",
        type=TaskType.DEVELOPMENT
    )
    
    mobile_agent.execute_task(app_task)
    logger.end_chapter("Mobile app completed")
    
    # Step 4: Cloud deployment
    logger.start_chapter("Cloud Deployment", "Deploy to cloud")
    cloud_agent = registry.create_agent("cloud_architect", logger)
    
    deploy_task = Task(
        id="cloud-001",
        title="Deploy game infrastructure",
        description="Set up scalable cloud infrastructure for the game",
        type=TaskType.INFRASTRUCTURE
    )
    
    cloud_agent.execute_task(deploy_task)
    logger.end_chapter("Deployment complete")
    
    # Generate collaboration report
    summary = logger.get_session_summary()
    print(f"\nCollaboration Summary:")
    print(f"- Chapters completed: {len(summary['chapters'])}")
    print(f"- Total duration: {summary['total_duration']}")
    print(f"- Agents involved: 4")


class SpecializedTestAgent(BaseAgent):
    """Example of a highly specialized custom agent"""
    
    def __init__(self, logger: ChapterLogger = None):
        super().__init__(
            name="AccessibilityExpert",
            role="Accessibility Specialist",
            logger=logger
        )
    
    def get_system_prompt(self) -> str:
        return """You are an Accessibility Expert specializing in making applications
accessible to all users. Your expertise includes:

- WCAG 2.1 guidelines and compliance
- Screen reader optimization
- Keyboard navigation implementation
- Color contrast and visual accessibility
- ARIA labels and semantic HTML
- Accessibility testing tools
- Alternative text and descriptions
- Accessible forms and error handling

You ensure all users can effectively use the applications you work on."""
    
    def get_specialties(self) -> List[str]:
        return [
            "WCAG compliance",
            "screen readers",
            "keyboard navigation",
            "ARIA",
            "accessibility testing",
            "semantic HTML",
            "inclusive design"
        ]
    
    def should_handle_task(self, task_description: str) -> bool:
        """Custom logic for task assignment"""
        keywords = [
            "accessibility", "a11y", "wcag", "screen reader",
            "keyboard", "aria", "inclusive", "disability"
        ]
        return any(keyword in task_description.lower() for keyword in keywords)


if __name__ == "__main__":
    print("Batman Incorporated - Custom Agents Examples\n")
    
    # Run examples
    example_custom_agent_usage()
    example_extending_batman()
    example_agent_collaboration()
    
    # Show specialized agent
    print("\n=== Specialized Agent Example ===")
    accessibility_agent = SpecializedTestAgent()
    print(f"Agent: {accessibility_agent.name}")
    print(f"Role: {accessibility_agent.role}")
    print(f"Specialties: {', '.join(accessibility_agent.get_specialties())}")
    
    # Test task assignment
    test_tasks = [
        "Add accessibility features to the dashboard",
        "Optimize database queries",
        "Ensure WCAG 2.1 compliance"
    ]
    
    print("\nTask assignment test:")
    for task in test_tasks:
        should_handle = accessibility_agent.should_handle_task(task)
        print(f"- '{task}': {'✓' if should_handle else '✗'}")
    
    print("\n✓ Custom agent examples completed!")