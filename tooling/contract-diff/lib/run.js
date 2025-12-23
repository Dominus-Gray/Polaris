#!/usr/bin/env node
"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.run = run;
const path = __importStar(require("path"));
const loadSchemas_1 = require("./loadSchemas");
const diffSchemas_1 = require("./diffSchemas");
const classify_1 = require("./classify");
const writeReport_1 = require("./writeReport");
function run(options = {}) {
    const { oldDir = 'schemas', newDir = 'schemas', output = 'contract-diff-report.json', versionFile = 'schemas/openapi/version.json' } = options;
    console.log('🔍 Contract Diff Analysis Started');
    console.log(`📁 Comparing schemas in: ${newDir}`);
    try {
        // Resolve paths relative to current working directory
        const resolvedOldDir = path.resolve(oldDir);
        const resolvedNewDir = path.resolve(newDir);
        const resolvedOutput = path.resolve(output);
        const resolvedVersionFile = path.resolve(versionFile);
        // For a single directory analysis, we compare against empty (all changes are additions)
        const oldSchemas = oldDir === newDir ? [] : (0, loadSchemas_1.loadSchemas)(resolvedOldDir);
        const newSchemas = (0, loadSchemas_1.loadSchemas)(resolvedNewDir);
        console.log(`📊 Loaded ${oldSchemas.length} old schemas and ${newSchemas.length} new schemas`);
        // Generate diff
        const changes = (0, diffSchemas_1.diffSchemas)(oldSchemas, newSchemas);
        console.log(`🔄 Found ${changes.length} changes`);
        // Classify changes
        const classification = (0, classify_1.classify)(changes);
        // Get current version
        const currentVersion = (0, writeReport_1.loadCurrentVersion)(resolvedVersionFile);
        // Generate report
        const report = (0, writeReport_1.writeReport)(classification, currentVersion, resolvedOutput);
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
    }
    catch (error) {
        console.error('❌ Contract diff analysis failed:', error);
        process.exit(1);
    }
}
// CLI execution
if (require.main === module) {
    const args = process.argv.slice(2);
    const options = {};
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
