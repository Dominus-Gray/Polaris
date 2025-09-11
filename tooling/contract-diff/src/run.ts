#!/usr/bin/env node

import * as path from 'path';
import { loadSchemas } from './loadSchemas';
import { diffSchemas } from './diffSchemas';
import { classify } from './classify';
import { writeReport, loadCurrentVersion } from './writeReport';

interface RunOptions {
  oldDir?: string;
  newDir?: string;
  output?: string;
  versionFile?: string;
}

export function run(options: RunOptions = {}): void {
  const {
    oldDir = 'schemas',
    newDir = 'schemas', 
    output = 'contract-diff-report.json',
    versionFile = 'schemas/openapi/version.json'
  } = options;
  
  console.log('🔍 Contract Diff Analysis Started');
  console.log(`📁 Comparing schemas in: ${newDir}`);
  
  try {
    // Resolve paths relative to current working directory
    const resolvedOldDir = path.resolve(oldDir);
    const resolvedNewDir = path.resolve(newDir);
    const resolvedOutput = path.resolve(output);
    const resolvedVersionFile = path.resolve(versionFile);
    
    // For a single directory analysis, we compare against empty (all changes are additions)
    const oldSchemas = oldDir === newDir ? [] : loadSchemas(resolvedOldDir);
    const newSchemas = loadSchemas(resolvedNewDir);
    
    console.log(`📊 Loaded ${oldSchemas.length} old schemas and ${newSchemas.length} new schemas`);
    
    // Generate diff
    const changes = diffSchemas(oldSchemas, newSchemas);
    console.log(`🔄 Found ${changes.length} changes`);
    
    // Classify changes
    const classification = classify(changes);
    
    // Get current version
    const currentVersion = loadCurrentVersion(resolvedVersionFile);
    
    // Generate report
    const report = writeReport(classification, currentVersion, resolvedOutput);
    
    // Print summary
    console.log('\n📋 Analysis Summary:');
    console.log(`   Breaking changes: ${report.summary.breakingCount}`);
    console.log(`   Additive changes: ${report.summary.additiveCount}`);
    console.log(`   Docs-only changes: ${report.summary.docsOnlyCount}`);
    console.log(`   Refactor changes: ${report.summary.refactorCount}`);
    console.log(`   Total changes: ${report.summary.totalChanges}`);
    
    console.log(`\n📈 Version Impact:`);
    console.log(`   Current version: ${report.version.current}`);
    console.log(`   Required bump: ${report.version.requiredBump}`);
    console.log(`   Suggested version: ${report.version.suggestedNew}`);
    
    console.log(`\n📄 Report written to: ${resolvedOutput}`);
    
    if (report.summary.breakingCount > 0) {
      console.log('\n⚠️  WARNING: Breaking changes detected!');
      report.breaking.forEach((change, index) => {
        console.log(`   ${index + 1}. ${change.type.toUpperCase()} ${change.path.join('.')}`);
      });
    }
    
  } catch (error) {
    console.error('❌ Contract diff analysis failed:', error);
    process.exit(1);
  }
}

// CLI execution
if (require.main === module) {
  const args = process.argv.slice(2);
  const options: RunOptions = {};
  
  for (let i = 0; i < args.length; i += 2) {
    const flag = args[i];
    const value = args[i + 1];
    
    switch (flag) {
      case '--old-dir':
        options.oldDir = value;
        break;
      case '--new-dir':
        options.newDir = value;
        break;
      case '--output':
        options.output = value;
        break;
      case '--version-file':
        options.versionFile = value;
        break;
      case '--help':
        console.log(`
Contract Diff Tool

Usage: node run.js [options]

Options:
  --old-dir <path>       Directory with old schemas (default: schemas)
  --new-dir <path>       Directory with new schemas (default: schemas)
  --output <path>        Output report file (default: contract-diff-report.json)
  --version-file <path>  Version file path (default: schemas/openapi/version.json)
  --help                 Show this help message
        `);
        process.exit(0);
    }
  }
  
  run(options);
}