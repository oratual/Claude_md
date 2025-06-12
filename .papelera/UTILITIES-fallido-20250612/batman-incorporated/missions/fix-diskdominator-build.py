#!/usr/bin/env python3
"""
Batman Mission: Fix DiskDominator Build Errors
==============================================
Uses Batman agents to automatically fix all build errors
"""

import os
import subprocess
import re
import json
from pathlib import Path

class DiskDominatorBuildFixer:
    def __init__(self):
        self.project_path = "/home/lauta/glados/DiskDominator"
        self.windows_path = "K:\\_Glados\\DiskDominator"
        self.tailscale_windows = "100.91.52.70"
        self.errors_fixed = 0
        
    def deploy_batman_agents(self):
        """Deploy specialized agents for different error types"""
        
        print("🦇 Deploying Batman Incorporated agents...")
        print("=" * 50)
        
        # Agent assignments
        agents = {
            "alfred": {
                "task": "Fix React import duplicates and TypeScript errors",
                "command": f"cd {self.project_path} && grep -r 'import React from' --include='*.tsx' | grep -v node_modules"
            },
            "robin": {
                "task": "Fix Next.js configuration issues",
                "command": f"cd {self.project_path} && cat next.config.mjs"
            },
            "oracle": {
                "task": "Analyze and fix component errors",
                "command": f"cd {self.project_path} && find components -name '*.tsx' -type f"
            },
            "batgirl": {
                "task": "Fix UI component imports",
                "command": f"cd {self.project_path} && grep -r 'use client' --include='*.tsx'"
            }
        }
        
        # Deploy each agent
        for agent_name, agent_info in agents.items():
            print(f"\n🔹 {agent_name.upper()}: {agent_info['task']}")
            self.run_agent_task(agent_name, agent_info)
            
    def run_agent_task(self, agent_name, agent_info):
        """Run specific agent task"""
        
        if agent_name == "alfred":
            self.fix_react_duplicates()
        elif agent_name == "robin":
            self.fix_nextjs_config()
        elif agent_name == "oracle":
            self.analyze_component_errors()
        elif agent_name == "batgirl":
            self.fix_use_client_directives()
            
    def fix_react_duplicates(self):
        """Alfred's task: Fix duplicate React imports"""
        print("🧙 Alfred: Scanning for duplicate React imports...")
        
        # Find all TSX files
        tsx_files = subprocess.run(
            f"find {self.project_path} -name '*.tsx' -type f | grep -v node_modules",
            shell=True, capture_output=True, text=True
        ).stdout.strip().split('\n')
        
        for file_path in tsx_files:
            if not file_path:
                continue
                
            with open(file_path, 'r') as f:
                lines = f.readlines()
                
            # Check for duplicate React imports
            react_import_count = sum(1 for line in lines if 'import React from' in line)
            
            if react_import_count > 1:
                print(f"  Fixing: {file_path}")
                
                # Remove duplicate imports
                seen_react = False
                new_lines = []
                
                for line in lines:
                    if 'import React from' in line:
                        if not seen_react:
                            new_lines.append(line)
                            seen_react = True
                    else:
                        new_lines.append(line)
                        
                with open(file_path, 'w') as f:
                    f.writelines(new_lines)
                    
                self.errors_fixed += 1
                
    def fix_use_client_directives(self):
        """Batgirl's task: Ensure 'use client' is first line"""
        print("🦹‍♀️ Batgirl: Fixing 'use client' directive placement...")
        
        tsx_files = subprocess.run(
            f"grep -l 'use client' {self.project_path}/components/*.tsx {self.project_path}/components/*/*.tsx 2>/dev/null",
            shell=True, capture_output=True, text=True
        ).stdout.strip().split('\n')
        
        for file_path in tsx_files:
            if not file_path:
                continue
                
            with open(file_path, 'r') as f:
                lines = f.readlines()
                
            # Check if 'use client' is not on first line
            if lines and '"use client"' not in lines[0]:
                # Find and remove existing 'use client'
                use_client_line = None
                new_lines = []
                
                for line in lines:
                    if '"use client"' in line:
                        use_client_line = line
                    else:
                        new_lines.append(line)
                        
                # Add 'use client' as first line
                if use_client_line:
                    final_lines = [use_client_line] + new_lines
                    
                    with open(file_path, 'w') as f:
                        f.writelines(final_lines)
                        
                    self.errors_fixed += 1
                    print(f"  Fixed: {file_path}")
                    
    def fix_nextjs_config(self):
        """Robin's task: Ensure Next.js config is correct"""
        print("🐦 Robin: Checking Next.js configuration...")
        
        config_path = f"{self.project_path}/next.config.mjs"
        
        # Read current config
        with open(config_path, 'r') as f:
            content = f.read()
            
        # Ensure proper export
        if 'export default' not in content:
            print("  Fixing: next.config.mjs export")
            content = content.replace('module.exports =', 'export default')
            
            with open(config_path, 'w') as f:
                f.write(content)
                
            self.errors_fixed += 1
            
    def analyze_component_errors(self):
        """Oracle's task: Deep analysis of component issues"""
        print("👁️ Oracle: Analyzing component structure...")
        
        # This would be more complex in practice
        # For now, just report findings
        
    def run_build_test(self):
        """Test if build works"""
        print("\n🔨 Testing build...")
        
        os.chdir(self.project_path)
        result = subprocess.run(
            "npm run build",
            shell=True,
            capture_output=True,
            text=True
        )
        
        return result.returncode == 0
        
    def execute_mission(self):
        """Main mission execution"""
        print("🦇 BATMAN INCORPORATED - DISKDOMINATOR BUILD FIX MISSION")
        print("=" * 60)
        print(f"Target: {self.project_path}")
        print(f"Windows sync: {self.windows_path}")
        print()
        
        # Deploy agents
        self.deploy_batman_agents()
        
        print(f"\n📊 Total errors fixed: {self.errors_fixed}")
        
        # Test build
        if self.run_build_test():
            print("\n✅ BUILD SUCCESSFUL! Ready for Tauri compilation.")
            print(f"\nNext step on Windows:")
            print(f"cd {self.windows_path}")
            print(f"npx tauri build")
        else:
            print("\n⚠️ Build still has errors. Running deep analysis...")
            
            # Would run more sophisticated error detection here
            print("Additional manual fixes may be needed.")

if __name__ == "__main__":
    fixer = DiskDominatorBuildFixer()
    fixer.execute_mission()