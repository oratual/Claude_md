"""
AI Orchestrator - Intelligent Task Planning and Agent Coordination
Uses Claude to analyze requirements and create sophisticated execution plans.
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import yaml

from core.task import Task, TaskType, TaskPriority, TaskStatus
from core.config import Config
from features.chapter_logger import ChapterLogger


class AIOrchestrator:
    """
    AI-powered orchestration engine that uses Claude for intelligent decision making.
    This is the brain of Batman Incorporated's evolution.
    """
    
    def __init__(self, config: Config, logger: ChapterLogger):
        """
        Initialize the AI Orchestrator.
        
        Args:
            config: System configuration
            logger: Chapter logger for narrative logging
        """
        self.config = config
        self.logger = logger
        self.analysis_history = []
        self.coordination_decisions = []
        
        # Load agent expertise profiles
        self.agent_profiles = self._load_agent_profiles()
        
    def _load_agent_profiles(self) -> Dict[str, Dict]:
        """Load detailed agent expertise profiles for better task assignment."""
        return {
            'alfred': {
                'role': 'Senior Developer',
                'strengths': ['backend', 'apis', 'architecture', 'databases', 'security'],
                'languages': ['python', 'node.js', 'go', 'java'],
                'complexity_threshold': 0.8,  # Can handle very complex tasks
                'parallel_capacity': 2  # Can work on 2 tasks simultaneously
            },
            'batgirl': {
                'role': 'Frontend Specialist',
                'strengths': ['ui/ux', 'react', 'vue', 'frontend', 'accessibility', 'responsive'],
                'languages': ['javascript', 'typescript', 'css', 'html'],
                'complexity_threshold': 0.7,
                'parallel_capacity': 2
            },
            'robin': {
                'role': 'DevOps & Junior Dev',
                'strengths': ['automation', 'ci/cd', 'scripts', 'deployment', 'monitoring'],
                'languages': ['bash', 'python', 'yaml', 'docker'],
                'complexity_threshold': 0.5,
                'parallel_capacity': 3  # Can handle more simple tasks
            },
            'oracle': {
                'role': 'QA & Security',
                'strengths': ['testing', 'security', 'quality', 'validation', 'documentation'],
                'languages': ['python', 'javascript', 'security-tools'],
                'complexity_threshold': 0.7,
                'parallel_capacity': 2
            },
            'lucius': {
                'role': 'Research & Innovation',
                'strengths': ['research', 'optimization', 'ai/ml', 'performance', 'new-tech'],
                'languages': ['python', 'r', 'julia', 'research-tools'],
                'complexity_threshold': 0.6,
                'parallel_capacity': 1  # Deep focus on single tasks
            }
        }
    
    def analyze_and_plan(self, user_request: str, context: Dict = None) -> List[Task]:
        """
        Use Claude to analyze user request and create an intelligent task plan.
        
        Args:
            user_request: Natural language description from user
            context: Additional context (current project state, files, etc.)
            
        Returns:
            List of intelligently planned tasks with dependencies
        """
        self.logger.log("🧠 Iniciando análisis AI-powered del requerimiento...")
        
        # Build comprehensive analysis prompt
        analysis_prompt = self._build_analysis_prompt(user_request, context)
        
        # Execute Claude for analysis
        success, analysis_result = self._execute_claude_analysis(analysis_prompt)
        
        if not success:
            self.logger.log("❌ Error en análisis AI, usando fallback básico")
            return self._fallback_task_planning(user_request)
        
        # Parse Claude's analysis into tasks
        tasks = self._parse_analysis_to_tasks(analysis_result, user_request)
        
        # Store analysis for learning
        self.analysis_history.append({
            'timestamp': datetime.now().isoformat(),
            'request': user_request,
            'analysis': analysis_result,
            'tasks_generated': len(tasks)
        })
        
        self.logger.log(f"✅ Plan generado: {len(tasks)} tareas con dependencias inteligentes")
        return tasks
    
    def _build_analysis_prompt(self, user_request: str, context: Dict = None) -> str:
        """Build a comprehensive prompt for Claude to analyze the request."""
        prompt_parts = [
            "You are an expert software architect analyzing a development request.",
            "Your task is to break down the following request into specific, actionable tasks.",
            "",
            "## User Request",
            f'"{user_request}"',
            ""
        ]
        
        # Add context if available
        if context:
            prompt_parts.extend([
                "## Current Project Context",
                f"- Project Type: {context.get('project_type', 'Unknown')}",
                f"- Technology Stack: {', '.join(context.get('tech_stack', []))}",
                f"- Existing Files: {context.get('file_count', 0)}",
                f"- Last Modified: {context.get('last_modified', 'Unknown')}",
                ""
            ])
        
        # Add agent profiles for smart assignment
        prompt_parts.extend([
            "## Available Agents and Their Expertise",
            ""
        ])
        
        for agent_name, profile in self.agent_profiles.items():
            prompt_parts.append(f"### {agent_name.capitalize()} - {profile['role']}")
            prompt_parts.append(f"- Strengths: {', '.join(profile['strengths'])}")
            prompt_parts.append(f"- Languages: {', '.join(profile['languages'])}")
            prompt_parts.append("")
        
        # Instructions for analysis
        prompt_parts.extend([
            "## Instructions",
            "1. Analyze the request and break it into specific development tasks",
            "2. For each task, determine:",
            "   - Title (clear and concise)",
            "   - Description (detailed explanation)",
            "   - Type (development/testing/documentation/infrastructure)",
            "   - Priority (1-5, where 5 is highest)",
            "   - Estimated hours",
            "   - Best agent to assign based on their expertise",
            "   - Dependencies on other tasks (if any)",
            "   - Potential risks or challenges",
            "",
            "3. Consider task parallelization opportunities",
            "4. Ensure logical task ordering with proper dependencies",
            "5. Include testing and documentation tasks",
            "",
            "## Output Format",
            "Provide your analysis as a JSON array with the following structure:",
            "```json",
            "[",
            "  {",
            '    "title": "Task title",',
            '    "description": "Detailed description",',
            '    "type": "development|testing|documentation|infrastructure",',
            '    "priority": 1-5,',
            '    "estimated_hours": 0.5-8.0,',
            '    "assigned_to": "agent_name",',
            '    "depends_on_indices": [0, 1],  // indices of prerequisite tasks',
            '    "tags": ["backend", "api", "security"],',
            '    "risks": "Potential challenges or risks"',
            "  }",
            "]",
            "```",
            "",
            "Think step by step and create a comprehensive plan that ensures project success."
        ])
        
        return "\n".join(prompt_parts)
    
    def _execute_claude_analysis(self, prompt: str) -> Tuple[bool, str]:
        """Execute Claude for task analysis."""
        self.logger.log("🤖 Consultando a Claude para análisis inteligente...")
        
        try:
            # Save prompt for debugging
            prompt_file = Path(f"/tmp/ai_orchestrator_prompt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
            prompt_file.write_text(prompt, encoding='utf-8')
            
            # Execute Claude
            cmd = [
                'claude',
                '--print',
                '--dangerously-skip-permissions',
                '--max-turns', '1',  # Single response needed
                prompt
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120  # 2 minutes for analysis
            )
            
            if result.returncode == 0:
                # Extract JSON from response
                response = result.stdout
                
                # Find JSON block in response
                import re
                json_match = re.search(r'```json\s*([\s\S]*?)\s*```', response)
                
                if json_match:
                    json_str = json_match.group(1)
                    # Validate JSON
                    json.loads(json_str)  # This will raise if invalid
                    return True, json_str
                else:
                    self.logger.log("⚠️ No se encontró JSON válido en la respuesta")
                    return False, response
            else:
                self.logger.log(f"❌ Error ejecutando Claude: {result.stderr}")
                return False, result.stderr
                
        except subprocess.TimeoutExpired:
            self.logger.log("⏱️ Timeout en análisis AI")
            return False, "Timeout"
        except json.JSONDecodeError as e:
            self.logger.log(f"❌ Error parseando JSON: {e}")
            return False, str(e)
        except Exception as e:
            self.logger.log(f"💥 Error inesperado: {e}")
            return False, str(e)
    
    def _parse_analysis_to_tasks(self, analysis_json: str, original_request: str) -> List[Task]:
        """Parse Claude's JSON analysis into Task objects."""
        tasks = []
        
        try:
            task_data_list = json.loads(analysis_json)
            
            for idx, task_data in enumerate(task_data_list):
                # Create task with all available information
                task = Task(
                    title=task_data.get('title', f'Task {idx + 1}'),
                    description=task_data.get('description', ''),
                    type=self._parse_task_type(task_data.get('type', 'development')),
                    priority=self._parse_priority(task_data.get('priority', 3)),
                    assigned_to=task_data.get('assigned_to'),
                    estimated_hours=float(task_data.get('estimated_hours', 1.0)),
                    tags=task_data.get('tags', [])
                )
                
                # Store additional metadata
                task.metadata = {
                    'risks': task_data.get('risks', ''),
                    'ai_generated': True,
                    'generation_timestamp': datetime.now().isoformat()
                }
                
                tasks.append(task)
            
            # Process dependencies after all tasks are created
            for idx, task_data in enumerate(task_data_list):
                if 'depends_on_indices' in task_data:
                    for dep_idx in task_data['depends_on_indices']:
                        if 0 <= dep_idx < len(tasks):
                            tasks[idx].depends_on.append(tasks[dep_idx].id)
            
            return tasks
            
        except Exception as e:
            self.logger.log(f"⚠️ Error parseando tareas: {e}")
            return self._fallback_task_planning(original_request)
    
    def _parse_task_type(self, type_str: str) -> TaskType:
        """Parse task type string to enum."""
        type_map = {
            'development': TaskType.DEVELOPMENT,
            'testing': TaskType.TESTING,
            'documentation': TaskType.DOCUMENTATION,
            'infrastructure': TaskType.INFRASTRUCTURE,
            'bug_fix': TaskType.BUG_FIX,
            'feature': TaskType.FEATURE,
            'refactor': TaskType.REFACTOR,
            'research': TaskType.RESEARCH
        }
        return type_map.get(type_str.lower(), TaskType.DEVELOPMENT)
    
    def _parse_priority(self, priority_int: int) -> TaskPriority:
        """Parse priority integer to enum."""
        if priority_int >= 5:
            return TaskPriority.CRITICAL
        elif priority_int >= 4:
            return TaskPriority.HIGH
        elif priority_int >= 2:
            return TaskPriority.MEDIUM
        else:
            return TaskPriority.LOW
    
    def _fallback_task_planning(self, user_request: str) -> List[Task]:
        """Fallback to basic task planning if AI analysis fails."""
        self.logger.log("📋 Usando planificación básica de tareas")
        
        # Create a single main task
        main_task = Task(
            title=f"Implementar: {user_request[:50]}...",
            description=user_request,
            type=TaskType.DEVELOPMENT,
            priority=TaskPriority.HIGH,
            estimated_hours=4.0,
            assigned_to='alfred'  # Default to most capable agent
        )
        
        return [main_task]
    
    def coordinate_agents(self, tasks: List[Task], active_agents: Dict[str, Any]) -> Dict[str, List[Task]]:
        """
        Use AI to coordinate task distribution among agents.
        
        Args:
            tasks: List of tasks to distribute
            active_agents: Currently active agents and their status
            
        Returns:
            Optimized task distribution
        """
        self.logger.log("🎯 Coordinando distribución inteligente de tareas...")
        
        # Build coordination prompt
        coord_prompt = self._build_coordination_prompt(tasks, active_agents)
        
        # Get AI recommendation
        success, coordination_plan = self._execute_claude_coordination(coord_prompt)
        
        if success:
            distribution = self._parse_coordination_plan(coordination_plan, tasks)
        else:
            distribution = self._fallback_distribution(tasks)
        
        # Store coordination decision
        self.coordination_decisions.append({
            'timestamp': datetime.now().isoformat(),
            'task_count': len(tasks),
            'agents': list(active_agents.keys()),
            'distribution': {k: len(v) for k, v in distribution.items()}
        })
        
        return distribution
    
    def _build_coordination_prompt(self, tasks: List[Task], active_agents: Dict) -> str:
        """Build prompt for intelligent task coordination."""
        prompt_parts = [
            "You are coordinating a team of specialized AI agents for optimal task execution.",
            "",
            "## Available Agents and Current Status"
        ]
        
        for agent_name, status in active_agents.items():
            profile = self.agent_profiles.get(agent_name, {})
            prompt_parts.extend([
                f"### {agent_name.capitalize()}",
                f"- Role: {profile.get('role', 'Unknown')}",
                f"- Current Load: {status.get('current_tasks', 0)} tasks",
                f"- Capacity: {profile.get('parallel_capacity', 1)} parallel tasks",
                f"- Specialties: {', '.join(profile.get('strengths', []))}",
                ""
            ])
        
        prompt_parts.extend([
            "## Tasks to Distribute",
            ""
        ])
        
        for idx, task in enumerate(tasks):
            prompt_parts.extend([
                f"{idx + 1}. {task.title}",
                f"   - Type: {task.type.value}",
                f"   - Priority: {task.priority.value}",
                f"   - Est. Hours: {task.estimated_hours}",
                f"   - Tags: {', '.join(task.tags)}",
                f"   - Dependencies: {len(task.depends_on)} tasks",
                ""
            ])
        
        prompt_parts.extend([
            "## Coordination Guidelines",
            "1. Match tasks to agent expertise",
            "2. Balance workload considering capacity",
            "3. Respect task dependencies",
            "4. Prioritize critical tasks",
            "5. Consider parallel execution opportunities",
            "",
            "Provide optimal distribution as JSON:",
            "```json",
            "{",
            '  "alfred": [1, 3],  // task indices',
            '  "batgirl": [2],',
            '  "reasoning": "Explanation of distribution logic"',
            "}",
            "```"
        ])
        
        return "\n".join(prompt_parts)
    
    def _execute_claude_coordination(self, prompt: str) -> Tuple[bool, str]:
        """Execute Claude for coordination decisions."""
        # Similar to _execute_claude_analysis but for coordination
        return self._execute_claude_analysis(prompt)
    
    def _parse_coordination_plan(self, plan_json: str, tasks: List[Task]) -> Dict[str, List[Task]]:
        """Parse coordination plan from Claude."""
        try:
            plan_data = json.loads(plan_json)
            distribution = {}
            
            for agent_name, task_indices in plan_data.items():
                if agent_name == 'reasoning':
                    self.logger.log(f"📝 Razonamiento: {plan_data['reasoning']}")
                    continue
                    
                agent_tasks = []
                for idx in task_indices:
                    if 0 <= idx - 1 < len(tasks):  # Adjust for 1-based indexing
                        agent_tasks.append(tasks[idx - 1])
                
                if agent_tasks:
                    distribution[agent_name] = agent_tasks
            
            return distribution
            
        except Exception as e:
            self.logger.log(f"⚠️ Error parseando plan de coordinación: {e}")
            return self._fallback_distribution(tasks)
    
    def _fallback_distribution(self, tasks: List[Task]) -> Dict[str, List[Task]]:
        """Simple fallback distribution based on task assignment."""
        distribution = {}
        
        for task in tasks:
            agent = task.assigned_to or 'alfred'
            if agent not in distribution:
                distribution[agent] = []
            distribution[agent].append(task)
        
        return distribution
    
    def suggest_conflict_resolution(self, conflict_description: str) -> Dict[str, Any]:
        """
        Use AI to suggest resolution for conflicts between agents.
        
        Args:
            conflict_description: Description of the conflict
            
        Returns:
            AI-suggested resolution strategy
        """
        self.logger.log("🤝 Consultando AI para resolución de conflicto...")
        
        prompt = self._build_conflict_resolution_prompt(conflict_description)
        success, resolution = self._execute_claude_analysis(prompt)
        
        if success:
            try:
                return json.loads(resolution)
            except:
                return {
                    'strategy': 'merge_carefully',
                    'reasoning': 'Failed to parse AI suggestion, defaulting to careful merge'
                }
        else:
            return {
                'strategy': 'sequential_execution',
                'reasoning': 'AI unavailable, defaulting to sequential execution'
            }
    
    def _build_conflict_resolution_prompt(self, conflict_description: str) -> str:
        """Build prompt for conflict resolution."""
        return f"""
You are resolving a conflict between AI agents working on the same codebase.

## Conflict Description
{conflict_description}

## Available Resolution Strategies
1. merge_carefully - Manually merge changes with careful review
2. sequential_execution - Execute tasks one after another
3. partition_codebase - Assign different parts to different agents
4. collaborative_review - Have agents review each other's work
5. rollback_and_retry - Rollback and retry with better coordination

Analyze the conflict and suggest the best resolution strategy.

Provide response as JSON:
```json
{{
  "strategy": "strategy_name",
  "reasoning": "Detailed explanation",
  "implementation_steps": ["step1", "step2", "step3"]
}}
```
"""
    
    def learn_from_execution(self, execution_results: Dict[str, Any]):
        """
        Learn from execution results to improve future planning.
        
        Args:
            execution_results: Results from task execution
        """
        # Store results for future learning
        learning_data = {
            'timestamp': datetime.now().isoformat(),
            'results': execution_results,
            'analysis_history': len(self.analysis_history),
            'coordination_history': len(self.coordination_decisions)
        }
        
        # Save to learning file
        learning_file = Path.home() / '.glados' / 'batman-incorporated' / 'ai_learning.yaml'
        learning_file.parent.mkdir(parents=True, exist_ok=True)
        
        existing_data = []
        if learning_file.exists():
            with open(learning_file, 'r') as f:
                existing_data = yaml.safe_load(f) or []
        
        existing_data.append(learning_data)
        
        # Keep only last 100 entries
        if len(existing_data) > 100:
            existing_data = existing_data[-100:]
        
        with open(learning_file, 'w') as f:
            yaml.dump(existing_data, f)
        
        self.logger.log("📚 Datos de aprendizaje almacenados para mejorar futuras ejecuciones")