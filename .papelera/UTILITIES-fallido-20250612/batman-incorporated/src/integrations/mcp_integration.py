"""
Integración con Model Context Protocols (MCPs) para Batman Incorporated.
Permite compartir contexto entre agentes mediante MCP Memory y otros servers.
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class MCPIntegration:
    """
    Maneja la integración con MCPs para compartir contexto entre agentes.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.mcp_memory_path = Path.home() / ".batman" / "mcp_memory"
        self.mcp_memory_path.mkdir(parents=True, exist_ok=True)
        
        # Estado compartido entre agentes
        self.shared_state = {
            "tasks_completed": [],
            "files_modified": set(),
            "agent_knowledge": {},
            "errors_found": [],
            "decisions_made": []
        }
        
        # Cargar estado previo si existe
        self._load_shared_state()
    
    def _load_shared_state(self):
        """Carga el estado compartido desde disco."""
        state_file = self.mcp_memory_path / "shared_state.json"
        if state_file.exists():
            try:
                with open(state_file, 'r') as f:
                    loaded = json.load(f)
                    # Convertir listas a sets donde sea necesario
                    self.shared_state.update(loaded)
                    if 'files_modified' in loaded:
                        self.shared_state['files_modified'] = set(loaded['files_modified'])
            except Exception as e:
                print(f"Error cargando estado compartido: {e}")
    
    def _save_shared_state(self):
        """Guarda el estado compartido a disco."""
        state_file = self.mcp_memory_path / "shared_state.json"
        try:
            # Convertir sets a listas para JSON
            to_save = self.shared_state.copy()
            if 'files_modified' in to_save:
                to_save['files_modified'] = list(to_save['files_modified'])
            
            with open(state_file, 'w') as f:
                json.dump(to_save, f, indent=2)
        except Exception as e:
            print(f"Error guardando estado compartido: {e}")
    
    def share_task_completion(self, agent_name: str, task_id: str, result: Dict[str, Any]):
        """
        Comparte que un agente completó una tarea.
        
        Args:
            agent_name: Nombre del agente
            task_id: ID de la tarea
            result: Resultado de la tarea
        """
        completion = {
            "agent": agent_name,
            "task_id": task_id,
            "timestamp": datetime.now().isoformat(),
            "result": result
        }
        
        self.shared_state["tasks_completed"].append(completion)
        
        # Si hay archivos modificados, agregarlos
        if "files_modified" in result:
            self.shared_state["files_modified"].update(result["files_modified"])
        
        self._save_shared_state()
    
    def share_agent_knowledge(self, agent_name: str, knowledge_type: str, data: Any):
        """
        Comparte conocimiento específico de un agente.
        
        Args:
            agent_name: Nombre del agente
            knowledge_type: Tipo de conocimiento (e.g., "api_endpoints", "test_results")
            data: Datos a compartir
        """
        if agent_name not in self.shared_state["agent_knowledge"]:
            self.shared_state["agent_knowledge"][agent_name] = {}
        
        self.shared_state["agent_knowledge"][agent_name][knowledge_type] = {
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
        self._save_shared_state()
    
    def get_agent_knowledge(self, agent_name: Optional[str] = None, knowledge_type: Optional[str] = None) -> Dict:
        """
        Obtiene conocimiento compartido por agentes.
        
        Args:
            agent_name: Filtrar por agente específico
            knowledge_type: Filtrar por tipo de conocimiento
            
        Returns:
            Conocimiento filtrado
        """
        knowledge = self.shared_state.get("agent_knowledge", {})
        
        if agent_name:
            knowledge = knowledge.get(agent_name, {})
            if knowledge_type:
                return knowledge.get(knowledge_type, {})
            return knowledge
        
        return knowledge
    
    def share_error(self, agent_name: str, error_type: str, details: str):
        """Comparte un error encontrado para que otros agentes lo eviten."""
        error_entry = {
            "agent": agent_name,
            "type": error_type,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        
        self.shared_state["errors_found"].append(error_entry)
        self._save_shared_state()
    
    def share_decision(self, agent_name: str, decision: str, reasoning: str):
        """Comparte una decisión importante tomada por un agente."""
        decision_entry = {
            "agent": agent_name,
            "decision": decision,
            "reasoning": reasoning,
            "timestamp": datetime.now().isoformat()
        }
        
        self.shared_state["decisions_made"].append(decision_entry)
        self._save_shared_state()
    
    def get_files_modified(self) -> List[str]:
        """Obtiene la lista de archivos modificados por todos los agentes."""
        return list(self.shared_state.get("files_modified", set()))
    
    def get_recent_errors(self, limit: int = 10) -> List[Dict]:
        """Obtiene los errores más recientes encontrados."""
        errors = self.shared_state.get("errors_found", [])
        return errors[-limit:] if errors else []
    
    def get_recent_decisions(self, limit: int = 10) -> List[Dict]:
        """Obtiene las decisiones más recientes tomadas."""
        decisions = self.shared_state.get("decisions_made", [])
        return decisions[-limit:] if decisions else []
    
    def create_agent_context(self, agent_name: str, task: Any) -> Dict[str, Any]:
        """
        Crea contexto enriquecido para un agente basado en el conocimiento compartido.
        
        Args:
            agent_name: Nombre del agente
            task: Tarea actual
            
        Returns:
            Contexto enriquecido con información relevante
        """
        context = {
            "agent": agent_name,
            "task": {
                "id": task.id,
                "title": task.title,
                "type": task.type.value
            },
            "shared_knowledge": {}
        }
        
        # Agregar archivos modificados relevantes
        files_modified = self.get_files_modified()
        if files_modified:
            context["files_recently_modified"] = files_modified[:20]  # Últimos 20
        
        # Agregar errores recientes para evitar
        recent_errors = self.get_recent_errors(5)
        if recent_errors:
            context["recent_errors_to_avoid"] = recent_errors
        
        # Agregar decisiones relevantes
        recent_decisions = self.get_recent_decisions(5)
        if recent_decisions:
            context["recent_decisions"] = recent_decisions
        
        # Agregar conocimiento de otros agentes que podría ser útil
        all_knowledge = self.get_agent_knowledge()
        relevant_knowledge = {}
        
        # Filtrar conocimiento relevante según el tipo de tarea
        task_keywords = f"{task.title} {task.description}".lower()
        
        for other_agent, knowledge_types in all_knowledge.items():
            if other_agent == agent_name:
                continue  # Skip propio conocimiento
                
            for k_type, k_data in knowledge_types.items():
                # Simple relevancia: si el tipo de conocimiento contiene palabras de la tarea
                if any(word in k_type.lower() for word in task_keywords.split()):
                    if other_agent not in relevant_knowledge:
                        relevant_knowledge[other_agent] = {}
                    relevant_knowledge[other_agent][k_type] = k_data
        
        if relevant_knowledge:
            context["shared_knowledge"] = relevant_knowledge
        
        return context
    
    def create_mcp_prompt_section(self, context: Dict[str, Any]) -> str:
        """
        Crea una sección de prompt con el contexto MCP para incluir en el prompt del agente.
        
        Args:
            context: Contexto creado por create_agent_context
            
        Returns:
            Sección de prompt formateada
        """
        prompt_parts = ["## Contexto Compartido (MCP Memory)\n"]
        
        # Archivos modificados recientemente
        if "files_recently_modified" in context:
            prompt_parts.append("### Archivos Modificados por Otros Agentes")
            for file in context["files_recently_modified"][:10]:
                prompt_parts.append(f"- {file}")
            prompt_parts.append("")
        
        # Errores a evitar
        if "recent_errors_to_avoid" in context:
            prompt_parts.append("### ⚠️ Errores Recientes a Evitar")
            for error in context["recent_errors_to_avoid"]:
                prompt_parts.append(f"- **{error['type']}** ({error['agent']}): {error['details']}")
            prompt_parts.append("")
        
        # Decisiones tomadas
        if "recent_decisions" in context:
            prompt_parts.append("### 📋 Decisiones Recientes de Otros Agentes")
            for decision in context["recent_decisions"]:
                prompt_parts.append(f"- **{decision['agent']}**: {decision['decision']}")
                prompt_parts.append(f"  _Razón: {decision['reasoning']}_")
            prompt_parts.append("")
        
        # Conocimiento compartido relevante
        if context.get("shared_knowledge"):
            prompt_parts.append("### 💡 Conocimiento Relevante de Otros Agentes")
            for agent, knowledge in context["shared_knowledge"].items():
                prompt_parts.append(f"\n**De {agent}:**")
                for k_type, k_data in knowledge.items():
                    prompt_parts.append(f"- {k_type}: {json.dumps(k_data['data'], indent=2)}")
            prompt_parts.append("")
        
        return "\n".join(prompt_parts)
    
    def clear_shared_state(self):
        """Limpia el estado compartido (útil para nuevas sesiones)."""
        self.shared_state = {
            "tasks_completed": [],
            "files_modified": set(),
            "agent_knowledge": {},
            "errors_found": [],
            "decisions_made": []
        }
        self._save_shared_state()


class MCPFileSystemIntegration:
    """
    Integración específica con MCP filesystem para operaciones optimizadas.
    """
    
    def __init__(self):
        self.mcp_available = self._check_mcp_availability()
    
    def _check_mcp_availability(self) -> bool:
        """Verifica si el MCP filesystem está disponible."""
        # Por ahora, asumimos que está disponible si Claude Code está activo
        # En el futuro, podríamos verificar la configuración real
        return True
    
    def suggest_file_operation(self, operation: str, path: str) -> str:
        """
        Sugiere usar MCP filesystem para operaciones de archivos.
        
        Args:
            operation: Tipo de operación (read, write, search, etc.)
            path: Ruta del archivo o directorio
            
        Returns:
            Sugerencia de comando MCP
        """
        suggestions = {
            "read": f"Usa MCP filesystem para leer {path} - más eficiente que Read tool",
            "write": f"Usa MCP filesystem para escribir {path} - operación atómica",
            "search": f"Usa MCP everything para buscar en {path} - búsqueda indexada",
            "list": f"Usa MCP filesystem para listar {path} - con metadatos completos"
        }
        
        return suggestions.get(operation, f"Considera usar MCP para {operation} en {path}")


# Singleton global
_mcp_instance = None

def get_mcp_integration(config: Optional[Dict] = None) -> MCPIntegration:
    """Obtiene la instancia global de MCPIntegration."""
    global _mcp_instance
    if _mcp_instance is None:
        _mcp_instance = MCPIntegration(config or {})
    return _mcp_instance