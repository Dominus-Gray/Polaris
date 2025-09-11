#!/usr/bin/env node

import * as fs from 'fs';
import * as path from 'path';
import * as yaml from 'js-yaml';

interface DiffReport {
  breaking: any[];
  additive: any[];
  docsOnly: any[];
  refactor: any[];
  version: {
    current: string;
    requiredBump: string;
    suggestedNew: string;
  };
  summary: {
    breakingCount: number;
    additiveCount: number;
    docsOnlyCount: number;
    refactorCount: number;
  };
}

interface DeprecationOverride {
  issueNumber: string;
  reason: string;
  impactedPaths: string[];
  approver: string;
  expiresAt?: string;
}

interface LinterConfig {
  deprecationWindowDays: number;
  enforcementMode: 'warn' | 'block';
  overrideFilePath: string;
  versionFilePath: string;
}

class ContractLinter {
  private config: LinterConfig;
  private hasErrors = false;
  private hasWarnings = false;
  
  constructor() {
    this.config = {
      deprecationWindowDays: parseInt(process.env.DEPRECATION_WINDOW_DAYS || '90'),
      enforcementMode: (process.env.DIFF_ENFORCEMENT_MODE || 'warn') as 'warn' | 'block',
      overrideFilePath: process.env.OVERRIDE_FILE_PATH || '.deprecation-override.yml',
      versionFilePath: 'schemas/openapi/version.json'
    };
  }
  
  public async enforceRules(reportPath: string): Promise<void> {
    console.log('🔍 Contract Linter - Enforcing governance rules');
    console.log(`📋 Enforcement mode: ${this.config.enforcementMode.toUpperCase()}`);
    
    try {
      // Load the diff report
      const report = this.loadReport(reportPath);
      
      // Load overrides if they exist
      const overrides = this.loadOverrides();
      
      // Run enforcement checks
      await this.checkVersionBumpRules(report);
      await this.checkDeprecationRules(report, overrides);
      await this.checkBreakingChangeRules(report, overrides);
      
      // Print summary and exit appropriately
      this.printSummary();
      this.exit();
      
    } catch (error) {
      this.error('Failed to run contract linter:', error);
      process.exit(1);
    }
  }
  
  private loadReport(reportPath: string): DiffReport {
    if (!fs.existsSync(reportPath)) {
      throw new Error(`Diff report not found: ${reportPath}`);
    }
    
    const reportContent = fs.readFileSync(reportPath, 'utf8');
    return JSON.parse(reportContent);
  }
  
  private loadOverrides(): DeprecationOverride[] {
    if (!fs.existsSync(this.config.overrideFilePath)) {
      return [];
    }
    
    try {
      const overrideContent = fs.readFileSync(this.config.overrideFilePath, 'utf8');
      const parsed = yaml.load(overrideContent) as any;
      return Array.isArray(parsed.overrides) ? parsed.overrides : [];
    } catch (error) {
      this.warn(`Failed to parse override file: ${error}`);
      return [];
    }
  }
  
  private async checkVersionBumpRules(report: DiffReport): Promise<void> {
    console.log('\n📈 Checking version bump rules...');
    
    // Load current version from version file
    let currentFileVersion = '1.0.0';
    try {
      if (fs.existsSync(this.config.versionFilePath)) {
        const versionData = JSON.parse(fs.readFileSync(this.config.versionFilePath, 'utf8'));
        currentFileVersion = versionData.apiVersion || '1.0.0';
      }
    } catch (error) {
      this.warn(`Failed to load version file: ${error}`);
    }
    
    // Check if the version bump matches the change requirements
    const requiredBump = report.version.requiredBump;
    const currentVersion = report.version.current;
    const suggestedVersion = report.version.suggestedNew;
    
    if (currentFileVersion !== currentVersion) {
      this.warn(`Version file mismatch: file shows ${currentFileVersion}, report shows ${currentVersion}`);
    }
    
    if (requiredBump !== 'none') {
      const message = `Changes require ${requiredBump} version bump (${currentVersion} → ${suggestedVersion})`;
      
      if (this.config.enforcementMode === 'block') {
        this.error(message);
      } else {
        this.warn(message);
      }
    } else {
      this.success('No version bump required');
    }
  }
  
  private async checkDeprecationRules(report: DiffReport, overrides: DeprecationOverride[]): Promise<void> {
    console.log('\\n⏰ Checking deprecation rules...');
    
    const removals = report.breaking.filter(change => change.type === 'remove');
    
    if (removals.length === 0) {
      this.success('No field/endpoint removals detected');
      return;
    }
    
    for (const removal of removals) {
      const path = removal.path.join('.');
      const hasOverride = this.checkOverrideForPath(path, overrides);
      
      if (hasOverride) {
        this.info(`Removal of ${path} allowed by override`);
        continue;
      }
      
      // Check if the removed field was properly deprecated
      const wasDeprecated = this.checkIfDeprecated(removal);
      
      if (!wasDeprecated) {
        const message = `Removal of ${path} without proper deprecation (requires ${this.config.deprecationWindowDays} day deprecation period)`;
        
        if (this.config.enforcementMode === 'block') {
          this.error(message);
        } else {
          this.warn(message);
        }
      } else {
        this.success(`Removal of ${path} follows deprecation policy`);
      }
    }
  }
  
  private async checkBreakingChangeRules(report: DiffReport, overrides: DeprecationOverride[]): Promise<void> {
    console.log('\\n💥 Checking breaking change rules...');
    
    if (report.summary.breakingCount === 0) {
      this.success('No breaking changes detected');
      return;
    }
    
    const unapprovedBreaking = report.breaking.filter(change => {
      const path = change.path.join('.');
      return !this.checkOverrideForPath(path, overrides);
    });
    
    if (unapprovedBreaking.length > 0) {
      const message = `${unapprovedBreaking.length} unapproved breaking changes detected`;
      
      if (this.config.enforcementMode === 'block') {
        this.error(message);
        unapprovedBreaking.forEach((change, index) => {
          console.log(`   ${index + 1}. ${change.type.toUpperCase()} ${change.path.join('.')}`);
        });
      } else {
        this.warn(message);
      }
    } else {
      this.success('All breaking changes have valid overrides');
    }
  }
  
  private checkOverrideForPath(path: string, overrides: DeprecationOverride[]): boolean {
    return overrides.some(override => {
      // Check if any override covers this path
      return override.impactedPaths.some(overridePath => {
        return path.startsWith(overridePath) || overridePath === '*';
      });
    });
  }
  
  private checkIfDeprecated(removal: any): boolean {
    // Check if the removed field had deprecation metadata
    if (removal.oldValue && typeof removal.oldValue === 'object') {
      return Boolean(
        removal.oldValue['x-status'] === 'deprecated' ||
        removal.oldValue['deprecated'] === true ||
        removal.oldValue['x-sunset']
      );
    }
    return false;
  }
  
  private success(message: string): void {
    console.log(`   ✅ ${message}`);
  }
  
  private info(message: string): void {
    console.log(`   ℹ️  ${message}`);
  }
  
  private warn(message: string): void {
    console.log(`   ⚠️  ${message}`);
    this.hasWarnings = true;
  }
  
  private error(message: string, error?: any): void {
    console.log(`   ❌ ${message}`);
    if (error) {
      console.log(`      ${error}`);
    }
    this.hasErrors = true;
  }
  
  private printSummary(): void {
    console.log('\\n📊 Linter Summary:');
    if (this.hasErrors) {
      console.log('   ❌ Errors found - contract changes violate governance rules');
    } else if (this.hasWarnings) {
      console.log('   ⚠️  Warnings found - please review contract changes');
    } else {
      console.log('   ✅ All governance rules passed');
    }
  }
  
  private exit(): void {
    if (this.hasErrors && this.config.enforcementMode === 'block') {
      process.exit(1);
    } else {
      process.exit(0);
    }
  }
}

// CLI execution
if (require.main === module) {
  const reportPath = process.argv[2] || 'contract-diff-report.json';
  const linter = new ContractLinter();
  linter.enforceRules(reportPath);
}