#!/usr/bin/env python3
"""
Batman v2 - The Orchestrator
Coordina a todo el equipo para misiones nocturnas.
"""

import argparse
import sys
import json
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from logger import get_logger
from orchestrator import BatmanOrchestrator, AllyType

logger = get_logger("batman")


class BatmanV2:
    """Batman v2 - El orquestador maestro."""
    
    def __init__(self):
        self.orchestrator = BatmanOrchestrator()
        self.mission_file = Path("missions/nightly.json")
        
    def night_patrol(self, skip_shutdown: bool = False):
        """Execute the nightly patrol - coordinate all allies."""
        logger.info("🌙 Batman starting Night Patrol...")
        
        # Load mission plan
        mission_plan = self._load_mission_plan()
        
        if not mission_plan:
            logger.error("No mission plan found!")
            return
        
        print("\n🦇 BATMAN NIGHT PATROL")
        print("=" * 50)
        print(f"Mission tasks: {len(mission_plan)}")
        print(f"Allies ready: Robin, Claude, Alfred, Oracle")
        print("=" * 50)
        
        # Execute mission
        results = self.orchestrator.coordinate_mission(mission_plan)
        
        # Generate and save report
        report = self.orchestrator.generate_mission_report(results)
        report_file = Path("logs") / f"mission_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        report_file.write_text(report)
        
        print("\n" + report)
        
        # System shutdown
        if not skip_shutdown:
            self._shutdown_system()
        else:
            print("\n✅ Night Patrol completed (shutdown skipped)")
    
    def _load_mission_plan(self) -> list:
        """Load the mission plan."""
        # Default mission if no file exists
        default_mission = [
            {
                "ally": "robin",
                "type": "execute",
                "files": ["tasks/robin-system.txt"],
                "name": "System maintenance",
                "wait": True
            },
            {
                "ally": "robin",
                "type": "clean",
                "days": 30,
                "name": "Clean old logs",
                "wait": True
            },
            {
                "ally": "claude",
                "project": "/home/lauta/glados/DiskDominator",
                "instructions": "Review code and fix any TODO comments",
                "name": "Code review",
                "wait": False
            },
            {
                "ally": "alfred",
                "type": "morning-report",
                "name": "Generate morning report",
                "wait": True
            }
        ]
        
        if self.mission_file.exists():
            try:
                with open(self.mission_file) as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading mission file: {e}")
        
        return default_mission
    
    def _shutdown_system(self):
        """Shutdown the system."""
        import time
        import os
        
        print("\n🌙 All missions completed. Shutting down system...")
        print("💤 Good night, Gotham!")
        
        time.sleep(5)
        
        try:
            if sys.platform == "linux":
                if Path("/proc/sys/fs/binfmt_misc/WSLInterop").exists():
                    logger.info("Shutting down Windows from WSL...")
                    os.system("powershell.exe -Command 'Stop-Computer -Force'")
                else:
                    logger.info("Shutting down Linux system...")
                    os.system("sudo shutdown -h now")
        except Exception as e:
            logger.error(f"Failed to shutdown: {e}")
    
    def deploy_ally(self, ally_name: str, task_config: dict):
        """Deploy a specific ally with task."""
        try:
            ally_type = AllyType(ally_name.lower())
            success = self.orchestrator.dispatch_ally(ally_type, task_config)
            
            if success:
                print(f"✅ {ally_name} deployed successfully")
                if task_config.get('wait', True):
                    self.orchestrator.wait_for_ally(ally_type)
            else:
                print(f"❌ Failed to deploy {ally_name}")
                
        except ValueError:
            print(f"❌ Unknown ally: {ally_name}")
            print(f"Available allies: {[a.value for a in AllyType]}")
    
    def status(self):
        """Show status of all allies."""
        print("\n🦇 BATMAN TEAM STATUS")
        print("=" * 50)
        
        for ally_type, ally in self.orchestrator.allies.items():
            status_icon = {
                "ready": "✅",
                "busy": "🔄",
                "error": "❌",
                "offline": "💤"
            }.get(ally.status.value, "❓")
            
            print(f"{status_icon} {ally_type.value.upper()}: {ally.status.value}")
            if ally.current_task:
                print(f"   Current task: {ally.current_task}")
        print("=" * 50)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Batman v2 - The Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start night patrol (with shutdown)
  batman-v2 night-patrol
  
  # Night patrol without shutdown
  batman-v2 night-patrol --no-shutdown
  
  # Deploy specific ally
  batman-v2 deploy robin --task execute --files tasks/robin-system.txt
  
  # Check team status
  batman-v2 status
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Night patrol
    patrol_parser = subparsers.add_parser('night-patrol', help='Start nightly patrol')
    patrol_parser.add_argument('--no-shutdown', action='store_true',
                              help='Skip system shutdown')
    
    # Deploy ally
    deploy_parser = subparsers.add_parser('deploy', help='Deploy specific ally')
    deploy_parser.add_argument('ally', help='Ally to deploy (robin, claude, alfred, oracle)')
    deploy_parser.add_argument('--task', required=True, help='Task type')
    deploy_parser.add_argument('--files', nargs='*', help='Task files')
    deploy_parser.add_argument('--project', help='Project path (for claude)')
    deploy_parser.add_argument('--instructions', help='Instructions (for claude)')
    deploy_parser.add_argument('--no-wait', action='store_true', help='Don\'t wait for completion')
    
    # Status
    status_parser = subparsers.add_parser('status', help='Show team status')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    batman = BatmanV2()
    
    try:
        if args.command == 'night-patrol':
            batman.night_patrol(skip_shutdown=args.no_shutdown)
            
        elif args.command == 'deploy':
            task_config = {
                'type': args.task,
                'name': f"{args.ally} {args.task}",
                'wait': not args.no_wait
            }
            
            if args.files:
                task_config['files'] = args.files
            if args.project:
                task_config['project'] = args.project
            if args.instructions:
                task_config['instructions'] = args.instructions
            
            batman.deploy_ally(args.ally, task_config)
            
        elif args.command == 'status':
            batman.status()
            
    except KeyboardInterrupt:
        logger.info("Mission aborted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Mission failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()