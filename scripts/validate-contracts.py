#!/usr/bin/env python3
"""
Contract Diff Pipeline Validator

This script validates the entire contract diff pipeline by:
1. Generating OpenAPI specifications
2. Running contract diff analysis
3. Validating policy enforcement
4. Testing various change scenarios

Usage:
    python scripts/validate-contracts.py [--test-breaking] [--output-dir PATH]

Options:
    --test-breaking   Test breaking change detection with synthetic changes
    --output-dir      Directory for test outputs (default: /tmp/contract-validation)
    --cleanup         Clean up test files after validation
    --verbose         Enable verbose output
    --help            Show this help message

Examples:
    # Run full validation suite
    python scripts/validate-contracts.py

    # Test breaking change detection  
    python scripts/validate-contracts.py --test-breaking --verbose
"""

import argparse
import json
import sys
import tempfile
from pathlib import Path
from typing import Dict, Any, List
import subprocess
import shutil


class ContractValidator:
    """Validates the contract diff pipeline functionality"""
    
    def __init__(self, output_dir: Path, verbose: bool = False):
        self.output_dir = output_dir
        self.verbose = verbose
        self.test_results: List[Dict[str, Any]] = []
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def log(self, message: str, level: str = "info") -> None:
        """Log message with level"""
        if level == "info":
            print(f"ℹ️  {message}")
        elif level == "success":
            print(f"✅ {message}")
        elif level == "warning":
            print(f"⚠️  {message}")
        elif level == "error":
            print(f"❌ {message}")
        elif level == "debug" and self.verbose:
            print(f"🔍 {message}")
    
    def run_command(self, cmd: List[str], description: str) -> tuple[bool, str]:
        """Run a command and capture output"""
        self.log(f"Running: {description}", "debug")
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                check=False,
                cwd=Path.cwd()
            )
            
            if result.returncode == 0:
                self.log(f"Command succeeded: {' '.join(cmd)}", "debug")
                return True, result.stdout
            else:
                self.log(f"Command failed: {' '.join(cmd)}", "debug")
                self.log(f"Error: {result.stderr}", "debug")
                return False, result.stderr
                
        except Exception as e:
            self.log(f"Exception running command: {e}", "error")
            return False, str(e)
    
    def validate_spec_generation(self) -> bool:
        """Test OpenAPI specification generation"""
        self.log("Testing OpenAPI specification generation...")
        
        # Test public-only generation
        success, output = self.run_command([
            "python", "scripts/generate-openapi-mock.py",
            "--public-only",
            "--output-dir", str(self.output_dir / "public-test")
        ], "Generate public-only spec")
        
        if not success:
            self.log("Failed to generate public-only specification", "error")
            return False
        
        # Verify output file exists and is valid JSON
        public_spec_file = self.output_dir / "public-test" / "public-v1.json"
        if not public_spec_file.exists():
            self.log("Public specification file not created", "error")
            return False
        
        try:
            with open(public_spec_file, 'r') as f:
                spec = json.load(f)
            
            # Basic validation
            required_fields = ['openapi', 'info', 'paths']
            for field in required_fields:
                if field not in spec:
                    self.log(f"Missing required field: {field}", "error")
                    return False
            
            self.log(f"Generated spec with {len(spec.get('paths', {}))} endpoints", "debug")
            
        except json.JSONDecodeError as e:
            self.log(f"Invalid JSON in generated spec: {e}", "error")
            return False
        
        # Test full generation (public + internal)
        success, output = self.run_command([
            "python", "scripts/generate-openapi-mock.py",
            "--output-dir", str(self.output_dir / "full-test")
        ], "Generate full specifications")
        
        if not success:
            self.log("Failed to generate full specifications", "error")
            return False
        
        # Verify both files exist
        public_file = self.output_dir / "full-test" / "public-v1.json"
        internal_file = self.output_dir / "full-test" / "internal-reference.json"
        
        if not public_file.exists() or not internal_file.exists():
            self.log("Full specification files not created", "error")
            return False
        
        self.log("OpenAPI specification generation validation passed", "success")
        return True
    
    def validate_diff_engine(self) -> bool:
        """Test contract diff engine"""
        self.log("Testing contract diff engine...")
        
        # Generate baseline specs
        baseline_dir = self.output_dir / "baseline"
        current_dir = self.output_dir / "current"
        
        success, _ = self.run_command([
            "python", "scripts/generate-openapi-mock.py",
            "--output-dir", str(baseline_dir)
        ], "Generate baseline specs")
        
        if not success:
            self.log("Failed to generate baseline specs", "error")
            return False
        
        # Create modified spec (copy and modify)
        shutil.copytree(baseline_dir, current_dir, dirs_exist_ok=True)
        
        # Modify the current spec to simulate changes
        current_spec_file = current_dir / "public-v1.json"
        with open(current_spec_file, 'r') as f:
            spec = json.load(f)
        
        # Add a new endpoint (additive change)
        spec['paths']['/api/test/new-endpoint'] = {
            "get": {
                "summary": "Test endpoint",
                "operationId": "test_new_endpoint",
                "responses": {
                    "200": {
                        "description": "Test response"
                    }
                }
            }
        }
        
        # Change version (informational change)
        spec['info']['version'] = '1.1.0'
        
        with open(current_spec_file, 'w') as f:
            json.dump(spec, f, indent=2)
        
        # Test diff engine
        diff_output = self.output_dir / "test-diff.json"
        success, output = self.run_command([
            "python", "scripts/diff-contracts.py",
            "--old-spec", str(baseline_dir / "public-v1.json"),
            "--new-spec", str(current_spec_file),
            "--format", "json",
            "--output", str(diff_output)
        ], "Run contract diff")
        
        if not success:
            self.log("Failed to run contract diff", "error")
            return False
        
        # Validate diff output
        try:
            with open(diff_output, 'r') as f:
                diff_report = json.load(f)
            
            # Should have detected changes
            if diff_report['summary']['total_changes'] == 0:
                self.log("Diff engine did not detect expected changes", "error")
                return False
            
            # Should have additive and informational changes
            if diff_report['summary']['additive_changes'] == 0:
                self.log("Did not detect expected additive changes", "warning")
            
            if diff_report['summary']['informational_changes'] == 0:
                self.log("Did not detect expected informational changes", "warning")
            
            # Should not have breaking changes
            if diff_report['summary']['breaking_changes'] > 0:
                self.log("Unexpected breaking changes detected", "warning")
            
            self.log(f"Detected {diff_report['summary']['total_changes']} changes as expected", "debug")
            
        except (json.JSONDecodeError, KeyError) as e:
            self.log(f"Invalid diff report format: {e}", "error")
            return False
        
        self.log("Contract diff engine validation passed", "success")
        return True
    
    def validate_breaking_change_detection(self) -> bool:
        """Test breaking change detection"""
        self.log("Testing breaking change detection...")
        
        # Generate baseline specs
        baseline_dir = self.output_dir / "breaking-baseline"
        breaking_dir = self.output_dir / "breaking-current"
        
        success, _ = self.run_command([
            "python", "scripts/generate-openapi-mock.py",
            "--output-dir", str(baseline_dir)
        ], "Generate baseline for breaking test")
        
        if not success:
            self.log("Failed to generate baseline for breaking test", "error")
            return False
        
        # Create spec with breaking changes
        shutil.copytree(baseline_dir, breaking_dir, dirs_exist_ok=True)
        
        breaking_spec_file = breaking_dir / "public-v1.json"
        with open(breaking_spec_file, 'r') as f:
            spec = json.load(f)
        
        # Remove an endpoint (breaking change)
        if '/api/health' in spec['paths']:
            del spec['paths']['/api/health']
        
        # Add required parameter (breaking change)
        if '/api/auth/login' in spec['paths'] and 'post' in spec['paths']['/api/auth/login']:
            login_post = spec['paths']['/api/auth/login']['post']
            if 'parameters' not in login_post:
                login_post['parameters'] = []
            
            login_post['parameters'].append({
                "name": "api_version",
                "in": "header",
                "required": True,
                "schema": {"type": "string"}
            })
        
        with open(breaking_spec_file, 'w') as f:
            json.dump(spec, f, indent=2)
        
        # Test breaking change detection
        diff_output = self.output_dir / "breaking-diff.json"
        success, output = self.run_command([
            "python", "scripts/diff-contracts.py",
            "--old-spec", str(baseline_dir / "public-v1.json"),
            "--new-spec", str(breaking_spec_file),
            "--format", "json",
            "--output", str(diff_output)
        ], "Detect breaking changes")
        
        # Should fail (exit code 1) due to breaking changes
        if success:
            self.log("Expected breaking change detection to fail but it passed", "warning")
        
        # Validate breaking changes were detected
        try:
            with open(diff_output, 'r') as f:
                diff_report = json.load(f)
            
            if diff_report['summary']['breaking_changes'] == 0:
                self.log("Failed to detect expected breaking changes", "error")
                return False
            
            self.log(f"Detected {diff_report['summary']['breaking_changes']} breaking changes as expected", "debug")
            
        except (json.JSONDecodeError, KeyError) as e:
            self.log(f"Invalid breaking diff report: {e}", "error")
            return False
        
        self.log("Breaking change detection validation passed", "success")
        return True
    
    def validate_output_formats(self) -> bool:
        """Test different output formats"""
        self.log("Testing output formats...")
        
        # Use existing baseline and current specs
        baseline_spec = self.output_dir / "baseline" / "public-v1.json"
        current_spec = self.output_dir / "current" / "public-v1.json"
        
        if not baseline_spec.exists() or not current_spec.exists():
            self.log("Baseline specs not found, skipping format validation", "warning")
            return True
        
        # Test text format
        text_output = self.output_dir / "diff-report.txt"
        success, output = self.run_command([
            "python", "scripts/diff-contracts.py",
            "--old-spec", str(baseline_spec),
            "--new-spec", str(current_spec),
            "--format", "text",
            "--output", str(text_output)
        ], "Generate text format diff")
        
        if not success or not text_output.exists():
            self.log("Failed to generate text format diff", "error")
            return False
        
        # Test JSON format (already tested above)
        json_output = self.output_dir / "diff-report.json"
        success, output = self.run_command([
            "python", "scripts/diff-contracts.py",
            "--old-spec", str(baseline_spec),
            "--new-spec", str(current_spec),
            "--format", "json",
            "--output", str(json_output)
        ], "Generate JSON format diff")
        
        if not success or not json_output.exists():
            self.log("Failed to generate JSON format diff", "error")
            return False
        
        # Validate JSON is parseable
        try:
            with open(json_output, 'r') as f:
                json.load(f)
        except json.JSONDecodeError as e:
            self.log(f"Invalid JSON output: {e}", "error")
            return False
        
        self.log("Output format validation passed", "success")
        return True
    
    def run_full_validation(self, test_breaking: bool = False) -> bool:
        """Run complete validation suite"""
        self.log("Starting contract diff pipeline validation...", "info")
        
        tests = [
            ("Spec Generation", self.validate_spec_generation),
            ("Diff Engine", self.validate_diff_engine),
            ("Output Formats", self.validate_output_formats),
        ]
        
        if test_breaking:
            tests.append(("Breaking Change Detection", self.validate_breaking_change_detection))
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            self.log(f"\n--- {test_name} ---")
            try:
                if test_func():
                    passed += 1
                else:
                    failed += 1
                    self.log(f"{test_name} FAILED", "error")
            except Exception as e:
                failed += 1
                self.log(f"{test_name} FAILED with exception: {e}", "error")
        
        self.log(f"\n=== Validation Summary ===")
        self.log(f"Passed: {passed}")
        self.log(f"Failed: {failed}")
        
        if failed == 0:
            self.log("All validations passed! 🎉", "success")
            return True
        else:
            self.log(f"{failed} validation(s) failed", "error")
            return False


def main():
    parser = argparse.ArgumentParser(
        description="Validate contract diff pipeline functionality",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split('Usage:')[1] if 'Usage:' in __doc__ else ''
    )
    
    parser.add_argument(
        '--test-breaking',
        action='store_true',
        help='Test breaking change detection'
    )
    
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path('/tmp/contract-validation'),
        help='Directory for test outputs'
    )
    
    parser.add_argument(
        '--cleanup',
        action='store_true',
        help='Clean up test files after validation'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    # Create validator and run tests
    validator = ContractValidator(args.output_dir, args.verbose)
    
    try:
        success = validator.run_full_validation(args.test_breaking)
        
        if args.cleanup:
            print(f"\n🧹 Cleaning up test files in {args.output_dir}")
            shutil.rmtree(args.output_dir, ignore_errors=True)
        else:
            print(f"\n📁 Test files preserved in: {args.output_dir}")
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n⏹️  Validation interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Validation failed with exception: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())