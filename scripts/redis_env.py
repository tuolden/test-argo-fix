#!/usr/bin/env python3
"""
🔐 Redis Environment Configuration

🎯 PURPOSE: Load environment variables from Redis for test_argo_fix
📝 USAGE: python3 redis_env.py [--export] [--json] [--key KEY]

🔧 WHAT IT DOES:
- Connects to Redis cluster for secrets
- Loads environment variables from 'env' hash
- Provides environment variables for application startup
- Supports export format for shell scripts

🤖 AI AGENT NOTES:
- Replaces traditional .env file approach  
- Uses centralized Redis secret management
- Automatically handles Redis connection and authentication
- Integrates with test_argo_fix application
"""

import argparse
import json
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from redis_secrets import RedisSecretsClient
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class RedisEnvLoader:
    """Loads environment variables from Redis for test_argo_fix."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.project_name = "test_argo_fix"
        
        # Default environment variables for test_argo_fix
        self.default_env = {
            "PROJECT_NAME": self.project_name,
            "ENVIRONMENT": "development", 
            "LOG_LEVEL": "INFO",
            "PORT": "8080",
            "HOST": "0.0.0.0"
        }
    
    def log(self, message: str, level: str = "INFO"):
        """Log message if verbose."""
        if self.verbose:
            if level == "ERROR":
                print(f"❌ {message}", file=sys.stderr)
            elif level == "SUCCESS":
                print(f"✅ {message}")
            else:
                print(f"ℹ️  {message}")
    
    def load_from_redis(self) -> dict:
        """Load environment variables from Redis."""
        if not REDIS_AVAILABLE:
            self.log("Redis client not available, using defaults only", "ERROR")
            return self.default_env
        
        try:
            self.log("Loading environment from Redis...")
            client = RedisSecretsClient(verbose=self.verbose)
            secrets = client.get_all_secrets()
            
            # Merge with defaults
            env_vars = {**self.default_env}
            
            # Map Redis secrets to environment variables
            secret_mappings = {
                "PGHOST": "DATABASE_HOST",
                "PGPORT": "DATABASE_PORT",
                "PGDATABASE": "DATABASE_NAME",
                "PGUSER": "DATABASE_USER",
                "PGPASSWORD": "DATABASE_PASSWORD",
                "GITHUB_PERSONAL_ACCESS_TOKEN": "GITHUB_TOKEN",
                "REDIS_PASSWORD": "REDIS_PASSWORD",
                # Direct passthroughs used by CI/deploy
                "REGISTRY_URL": "REGISTRY_URL",
            }

            for redis_key, env_key in secret_mappings.items():
                if redis_key in secrets:
                    env_vars[env_key] = secrets[redis_key]
                    self.log(f"Mapped {redis_key} -> {env_key}")
            
            # Add project-specific database URL
            if all(k in env_vars for k in ["DATABASE_HOST", "DATABASE_PORT", "DATABASE_NAME", "DATABASE_USER", "DATABASE_PASSWORD"]):
                env_vars["DATABASE_URL"] = (
                    f"postgresql://{env_vars['DATABASE_USER']}:{env_vars['DATABASE_PASSWORD']}"
                    f"@{env_vars['DATABASE_HOST']}:{env_vars['DATABASE_PORT']}/{env_vars['DATABASE_NAME']}"
                )
                self.log("Generated DATABASE_URL")
            
            self.log(f"Loaded {len(env_vars)} environment variables", "SUCCESS")
            return env_vars
            
        except Exception as e:
            self.log(f"Error loading from Redis: {e}", "ERROR")
            self.log("Falling back to default environment")
            return self.default_env
    
    def load_from_file(self, file_path: str = ".env") -> dict:
        """Load environment variables from .env file as fallback."""
        env_vars = {**self.default_env}
        
        if not os.path.exists(file_path):
            self.log(f"No {file_path} file found, using defaults")
            return env_vars
        
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip().strip('"').strip("'")
            
            self.log(f"Loaded {len(env_vars)} variables from {file_path}")
            return env_vars
        except Exception as e:
            self.log(f"Error loading {file_path}: {e}", "ERROR")
            return env_vars
    
    def get_environment(self, use_redis: bool = True, fallback_file: str = ".env") -> dict:
        """Get complete environment configuration."""
        if use_redis:
            return self.load_from_redis()
        else:
            return self.load_from_file(fallback_file)


def main():
    """Main entry point for CLI usage."""
    parser = argparse.ArgumentParser(
        description="Load environment variables for test_argo_fix from Redis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Load all environment variables
  python3 redis_env.py
  
  # Export format for shell
  python3 redis_env.py --export
  
  # JSON output
  python3 redis_env.py --json
  
  # Get specific variable
  python3 redis_env.py --key DATABASE_URL
  
  # Use .env file fallback
  python3 redis_env.py --no-redis
        """
    )
    
    parser.add_argument(
        "--export",
        action="store_true",
        help="Output in export format for shell evaluation"
    )
    
    parser.add_argument(
        "--json",
        action="store_true", 
        help="Output as JSON"
    )
    
    parser.add_argument(
        "--key",
        help="Get specific environment variable"
    )
    
    parser.add_argument(
        "--no-redis",
        action="store_true",
        help="Don't use Redis, load from .env file"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    try:
        loader = RedisEnvLoader(verbose=args.verbose)
        env_vars = loader.get_environment(use_redis=not args.no_redis)
        
        if args.key:
            # Get specific key
            if args.key in env_vars:
                print(env_vars[args.key])
                sys.exit(0)
            else:
                print(f"❌ Key '{args.key}' not found", file=sys.stderr)
                sys.exit(1)
        elif args.json:
            # JSON output
            print(json.dumps(env_vars, indent=2))
        elif args.export:
            # Export format
            for key, value in env_vars.items():
                print(f"export {key}='{value}'")
        else:
            # Standard key=value format
            for key, value in env_vars.items():
                print(f"{key}={value}")
                
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
