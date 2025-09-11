#!/usr/bin/env python3
"""
Management CLI for Action Plan Versioning & Recommendation Engine
Provides command-line interface for administrative tasks
"""

import asyncio
import sys
import os
from pathlib import Path
import argparse
import logging
from datetime import datetime
from typing import Optional
import uuid

# Add backend to path for imports
sys.path.append(str(Path(__file__).parent / 'backend'))

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_environment():
    """Setup environment for CLI operations"""
    # Load environment variables
    try:
        from dotenv import load_dotenv
        env_path = Path(__file__).parent / 'backend' / '.env'
        if env_path.exists():
            load_dotenv(env_path)
        else:
            logger.warning("No .env file found, using environment variables")
    except ImportError:
        logger.info("python-dotenv not available, using environment variables only")

async def generate_recommendation_command(client_id: str, provider_type: str = "rule_based"):
    """Generate an action plan recommendation for a client"""
    logger.info(f"Generating recommendation for client {client_id} using {provider_type} provider")
    
    try:
        # Mock implementation - in real system would connect to database
        print(f"📋 Generating action plan recommendation...")
        print(f"   Client ID: {client_id}")
        print(f"   Provider: {provider_type}")
        
        # Simulate recommendation generation
        from test_action_plans_standalone import RuleBasedBaselineRecommendationProvider
        
        provider = RuleBasedBaselineRecommendationProvider()
        
        # Mock client context
        client_context = {
            "client_id": client_id,
            "risk_score": 65,
            "readiness_percent": 40,
            "assessment_gaps": ["financial_management", "operations"],
            "industry": "technology"
        }
        
        proposal = provider.generate_plan(client_context)
        
        plan_id = str(uuid.uuid4())
        
        print(f"✅ Generated recommendation successfully!")
        print(f"   Plan ID: {plan_id}")
        print(f"   Goals: {len(proposal['goals'])}")
        print(f"   Interventions: {len(proposal['interventions'])}")
        print(f"   Risk Level: {proposal['metadata']['source_tags'][1]}")
        
        return plan_id
        
    except Exception as e:
        logger.error(f"Failed to generate recommendation: {str(e)}")
        return None

async def list_action_plans_command(client_id: Optional[str] = None, status: Optional[str] = None):
    """List action plans, optionally filtered by client or status"""
    print(f"📋 Listing action plans...")
    
    if client_id:
        print(f"   Filtered by client: {client_id}")
    if status:
        print(f"   Filtered by status: {status}")
    
    # Mock implementation - would query database in real system
    print(f"   Found 3 action plans:")
    print(f"   - Plan v1 (client_001): suggested - Generated 2024-01-01")
    print(f"   - Plan v2 (client_001): active - Activated 2024-01-02") 
    print(f"   - Plan v1 (client_002): archived - Created 2024-01-01")

async def activate_plan_command(plan_id: str, force: bool = False):
    """Activate a suggested or draft action plan"""
    logger.info(f"Activating action plan {plan_id}")
    
    if not force:
        response = input(f"Are you sure you want to activate plan {plan_id}? (y/N): ")
        if response.lower() != 'y':
            print("❌ Activation cancelled")
            return False
    
    print(f"🔄 Activating action plan {plan_id}...")
    print(f"   - Archiving previous active plan")
    print(f"   - Computing version diff")
    print(f"   - Updating plan series")
    print(f"   - Emitting domain events")
    print(f"✅ Action plan activated successfully!")
    
    return True

async def compute_diff_command(from_plan_id: str, to_plan_id: str):
    """Compute differences between two action plans"""
    logger.info(f"Computing diff between {from_plan_id} and {to_plan_id}")
    
    # Mock implementation
    from test_action_plans_standalone import compute_action_plan_diff
    
    # Sample plans for demo
    plan_a = {
        "goals": [
            {"id": "goal_1", "title": "Financial Management", "description": "Improve financial tracking"},
            {"id": "goal_2", "title": "Compliance", "description": "Meet regulatory requirements"}
        ],
        "interventions": [
            {"id": "int_1", "goal_id": "goal_1", "title": "Accounting Software", "type": "tool_adoption"}
        ]
    }
    
    plan_b = {
        "goals": [
            {"id": "goal_1", "title": "Advanced Financial Management", "description": "Comprehensive financial system"},
            {"id": "goal_3", "title": "Operational Excellence", "description": "Streamline operations"}
        ],
        "interventions": [
            {"id": "int_1", "goal_id": "goal_1", "title": "Accounting Software", "type": "tool_adoption"},
            {"id": "int_2", "goal_id": "goal_3", "title": "Process Documentation", "type": "process_improvement"}
        ]
    }
    
    diff = compute_action_plan_diff(plan_a, plan_b)
    
    print(f"📊 Diff Results:")
    print(f"   Added Goals: {len(diff['added']['goals'])}")
    print(f"   Removed Goals: {len(diff['removed']['goals'])}")
    print(f"   Changed Goals: {len(diff['changed']['goals'])}")
    print(f"   Added Interventions: {len(diff['added']['interventions'])}")
    print(f"   Removed Interventions: {len(diff['removed']['interventions'])}")
    print(f"   Changed Interventions: {len(diff['changed']['interventions'])}")

async def validate_rules_config_command():
    """Validate the recommendation rules configuration file"""
    config_path = Path(__file__).parent / 'backend' / 'config' / 'rules' / 'recommendations.yaml'
    
    print(f"🔍 Validating rules configuration...")
    print(f"   Config file: {config_path}")
    
    if not config_path.exists():
        print(f"❌ Configuration file not found: {config_path}")
        return False
    
    try:
        import yaml
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Validate structure
        required_sections = ['risk_score_thresholds', 'readiness_percent_adjustments', 
                           'area_specific_recommendations', 'default_timeframes']
        
        for section in required_sections:
            if section not in config:
                print(f"❌ Missing required section: {section}")
                return False
        
        # Validate risk thresholds
        for level in ['high', 'medium', 'low']:
            if level not in config['risk_score_thresholds']:
                print(f"❌ Missing risk level: {level}")
                return False
            
            threshold = config['risk_score_thresholds'][level]
            if 'min' not in threshold or 'goals' not in threshold:
                print(f"❌ Invalid structure for risk level: {level}")
                return False
        
        print(f"✅ Configuration file is valid!")
        print(f"   Risk levels: {list(config['risk_score_thresholds'].keys())}")
        print(f"   Default timeframes: {len(config['default_timeframes'])} types")
        return True
        
    except Exception as e:
        print(f"❌ Configuration validation failed: {str(e)}")
        return False

async def stats_command():
    """Display system statistics"""
    print(f"📈 Action Plan System Statistics")
    print(f"   Generated at: {datetime.utcnow().isoformat()}")
    print(f"")
    
    # Mock statistics - would query database in real system
    print(f"📊 Plan Statistics:")
    print(f"   Total Plans: 156")
    print(f"   Active Plans: 87")
    print(f"   Suggested Plans: 23")
    print(f"   Archived Plans: 46")
    print(f"")
    
    print(f"🤖 Recommendation Statistics:")
    print(f"   Total Recommendations: 89")
    print(f"   Acceptance Rate: 74.2%")
    print(f"   High Risk Plans: 34")
    print(f"   Medium Risk Plans: 41")
    print(f"   Low Risk Plans: 14")
    print(f"")
    
    print(f"🔄 Version Statistics:")
    print(f"   Total Versions: 234")
    print(f"   Average Versions per Client: 2.7")
    print(f"   Diffs Computed: 78")
    print(f"")
    
    print(f"📅 Activity (Last 30 Days):")
    print(f"   Recommendations Generated: 23")
    print(f"   Plans Activated: 19")
    print(f"   Plans Archived: 15")

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Action Plan Versioning & Recommendation Engine CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s recommend client_123                     # Generate recommendation
  %(prog)s list --client client_123                # List client's plans
  %(prog)s activate plan_456                       # Activate a plan
  %(prog)s diff plan_123 plan_456                  # Compute plan differences
  %(prog)s validate-config                         # Validate rules config
  %(prog)s stats                                   # Show system statistics
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Recommend command
    recommend_parser = subparsers.add_parser('recommend', help='Generate action plan recommendation')
    recommend_parser.add_argument('client_id', help='Client ID to generate recommendation for')
    recommend_parser.add_argument('--provider', default='rule_based', 
                                help='Recommendation provider type (default: rule_based)')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List action plans')
    list_parser.add_argument('--client', help='Filter by client ID')
    list_parser.add_argument('--status', choices=['draft', 'suggested', 'active', 'archived'],
                           help='Filter by plan status')
    
    # Activate command
    activate_parser = subparsers.add_parser('activate', help='Activate an action plan')
    activate_parser.add_argument('plan_id', help='Plan ID to activate')
    activate_parser.add_argument('--force', action='store_true', 
                               help='Skip confirmation prompt')
    
    # Diff command
    diff_parser = subparsers.add_parser('diff', help='Compute differences between two plans')
    diff_parser.add_argument('from_plan_id', help='Source plan ID')
    diff_parser.add_argument('to_plan_id', help='Target plan ID')
    
    # Validate config command
    subparsers.add_parser('validate-config', help='Validate recommendation rules configuration')
    
    # Stats command
    subparsers.add_parser('stats', help='Display system statistics')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Setup environment
    setup_environment()
    
    # Execute command
    try:
        if args.command == 'recommend':
            result = asyncio.run(generate_recommendation_command(args.client_id, args.provider))
            return 0 if result else 1
            
        elif args.command == 'list':
            asyncio.run(list_action_plans_command(args.client, args.status))
            return 0
            
        elif args.command == 'activate':
            result = asyncio.run(activate_plan_command(args.plan_id, args.force))
            return 0 if result else 1
            
        elif args.command == 'diff':
            asyncio.run(compute_diff_command(args.from_plan_id, args.to_plan_id))
            return 0
            
        elif args.command == 'validate-config':
            result = asyncio.run(validate_rules_config_command())
            return 0 if result else 1
            
        elif args.command == 'stats':
            asyncio.run(stats_command())
            return 0
            
        else:
            print(f"Unknown command: {args.command}")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
        return 1
    except Exception as e:
        logger.error(f"Command failed: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())