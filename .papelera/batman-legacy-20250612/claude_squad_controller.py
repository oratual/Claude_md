#!/usr/bin/env python3
"""
Claude Squad Controller for Batman
Prototype for controlling Claude Squad sessions from Python without modifying the Go code.
"""

import subprocess
import time
import json
import os
import re
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from datetime import datetime


class ClaudeSquadController:
    """Controller for managing Claude Squad sessions programmatically."""
    
    def __init__(self, cs_binary: str = "cs"):
        self.cs_binary = cs_binary
        self.config_dir = Path.home() / ".claude-squad"
        
    def _run_command(self, cmd: List[str], capture_output: bool = True) -> Tuple[int, str, str]:
        """Run a command and return (returncode, stdout, stderr)."""
        try:
            result = subprocess.run(
                cmd,
                capture_output=capture_output,
                text=True,
                check=False
            )
            return result.returncode, result.stdout, result.stderr
        except Exception as e:
            return -1, "", str(e)
    
    def _get_tmux_session_name(self, title: str) -> str:
        """Convert title to tmux session name format used by Claude Squad."""
        # Mimics toClaudeSquadTmuxName from Go code
        title = re.sub(r'\s+', '', title)
        title = title.replace('.', '_')
        return f"claudesquad_{title}"
    
    def create_instance(self, title: str, program: str = "claude", 
                       auto_yes: bool = True) -> bool:
        """Create a new Claude Squad instance."""
        cmd = [self.cs_binary]
        if program != "claude":
            cmd.extend(["--program", program])
        if auto_yes:
            cmd.append("--autoyes")
            
        # This would need to be done interactively or via expect
        # For now, we'll document this limitation
        print(f"Note: Creating instance '{title}' requires interactive input")
        print(f"Run: {' '.join(cmd)}")
        return False
    
    def list_instances(self) -> List[Dict]:
        """List all Claude Squad instances by reading the state file."""
        instances_file = self.config_dir / "instances.json"
        if not instances_file.exists():
            return []
            
        try:
            with open(instances_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading instances: {e}")
            return []
    
    def send_to_instance(self, title: str, text: str) -> bool:
        """Send text to a specific instance via tmux."""
        session_name = self._get_tmux_session_name(title)
        
        # Check if session exists
        ret, _, _ = self._run_command(["tmux", "has-session", "-t", session_name])
        if ret != 0:
            print(f"Session {session_name} not found")
            return False
        
        # Send keys to the session
        cmd = ["tmux", "send-keys", "-t", session_name, text, "Enter"]
        ret, _, err = self._run_command(cmd)
        
        if ret != 0:
            print(f"Error sending to session: {err}")
            return False
            
        return True
    
    def capture_output(self, title: str, lines: int = 100) -> Optional[str]:
        """Capture the current output from an instance."""
        session_name = self._get_tmux_session_name(title)
        
        # Capture pane content
        cmd = ["tmux", "capture-pane", "-t", session_name, "-p", "-S", f"-{lines}"]
        ret, stdout, err = self._run_command(cmd)
        
        if ret != 0:
            print(f"Error capturing output: {err}")
            return None
            
        return stdout
    
    def wait_for_prompt(self, title: str, timeout: int = 30) -> bool:
        """Wait for instance to be ready for input."""
        start_time = time.time()
        last_output = ""
        
        while time.time() - start_time < timeout:
            output = self.capture_output(title, lines=50)
            if output and output != last_output:
                last_output = output
                
                # Check for common prompts
                if any(prompt in output.lower() for prompt in [
                    "what would you like",
                    "how can i help",
                    "ready",
                    "> ",
                    ">>> "
                ]):
                    return True
                    
            time.sleep(1)
            
        return False
    
    def pause_instance(self, title: str) -> bool:
        """Pause an instance (requires interactive Claude Squad)."""
        # This would need to be done via the CS interface
        # For now, we can kill the tmux session as a workaround
        session_name = self._get_tmux_session_name(title)
        ret, _, _ = self._run_command(["tmux", "kill-session", "-t", session_name])
        return ret == 0
    
    def get_instance_status(self, title: str) -> Optional[str]:
        """Get the status of an instance."""
        instances = self.list_instances()
        for instance in instances:
            if instance.get("title") == title:
                status_map = {0: "Running", 1: "Ready", 2: "Loading", 3: "Paused"}
                return status_map.get(instance.get("status"), "Unknown")
        return None


class BatmanClaudeSquadTask:
    """Example task executor using Claude Squad."""
    
    def __init__(self, controller: ClaudeSquadController):
        self.controller = controller
        self.instance_title = f"batman-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
    def execute_task(self, prompts: List[str]) -> Dict[str, any]:
        """Execute a series of prompts and collect results."""
        results = {
            "instance": self.instance_title,
            "start_time": datetime.now().isoformat(),
            "prompts": [],
            "outputs": [],
            "success": False
        }
        
        print(f"Starting task with instance: {self.instance_title}")
        
        # Note: Instance creation would need to be done manually or via expect
        print("Please create instance manually with:")
        print(f"cs --autoyes  # Then name it '{self.instance_title}'")
        input("Press Enter when ready...")
        
        # Wait for instance to be ready
        if not self.controller.wait_for_prompt(self.instance_title):
            print("Instance not ready")
            return results
            
        # Execute prompts
        for i, prompt in enumerate(prompts):
            print(f"\nExecuting prompt {i+1}/{len(prompts)}: {prompt[:50]}...")
            
            # Send prompt
            if not self.controller.send_to_instance(self.instance_title, prompt):
                print("Failed to send prompt")
                break
                
            # Wait for response
            time.sleep(5)  # Give it time to process
            
            # Capture output
            output = self.controller.capture_output(self.instance_title)
            if output:
                results["prompts"].append(prompt)
                results["outputs"].append(output)
                
            # Wait for next prompt
            if i < len(prompts) - 1:
                self.controller.wait_for_prompt(self.instance_title)
                
        results["end_time"] = datetime.now().isoformat()
        results["success"] = len(results["outputs"]) == len(prompts)
        
        return results


def demo_automated_task():
    """Demonstrate automated task execution."""
    controller = ClaudeSquadController()
    
    # Example: Code review task
    task = BatmanClaudeSquadTask(controller)
    
    prompts = [
        "Please review this Python code for potential improvements:\n\ndef calculate_sum(numbers):\n    total = 0\n    for n in numbers:\n        total = total + n\n    return total",
        "Can you show me the optimized version?",
        "What about performance considerations for very large lists?"
    ]
    
    results = task.execute_task(prompts)
    
    # Save results
    output_file = f"batman-task-{results['instance']}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
        
    print(f"\nTask completed. Results saved to: {output_file}")
    
    return results


def monitor_instance_example():
    """Example of monitoring a Claude Squad instance."""
    controller = ClaudeSquadController()
    
    print("Current Claude Squad instances:")
    instances = controller.list_instances()
    
    for instance in instances:
        print(f"\nInstance: {instance.get('title')}")
        print(f"  Status: {instance.get('status')}")
        print(f"  Program: {instance.get('program')}")
        print(f"  Created: {instance.get('created_at')}")
        
        # Get current output
        output = controller.capture_output(instance.get('title'), lines=20)
        if output:
            print(f"  Recent output:")
            print("  " + "\n  ".join(output.strip().split('\n')[-5:]))


if __name__ == "__main__":
    print("Claude Squad Controller Demo")
    print("=" * 50)
    
    controller = ClaudeSquadController()
    
    # Check if Claude Squad is available
    ret, _, _ = controller._run_command([controller.cs_binary, "version"])
    if ret != 0:
        print("Error: Claude Squad (cs) not found in PATH")
        print("Please ensure Claude Squad is installed and accessible")
        exit(1)
        
    print("\nOptions:")
    print("1. Monitor existing instances")
    print("2. Run automated task demo")
    
    choice = input("\nSelect option (1-2): ")
    
    if choice == "1":
        monitor_instance_example()
    elif choice == "2":
        demo_automated_task()
    else:
        print("Invalid option")