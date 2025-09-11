import { ChangeClassification, DiffReport, VersionInfo } from './types';
import * as fs from 'fs';
import * as path from 'path';

export function writeReport(classification: ChangeClassification, currentVersion: string, outputPath: string = 'contract-diff-report.json'): DiffReport {
  const versionInfo = calculateVersionBump(classification, currentVersion);
  
  const report: DiffReport = {
    breaking: classification.breaking,
    additive: classification.additive,
    docsOnly: classification.docsOnly,
    refactor: classification.refactor,
    version: versionInfo,
    timestamp: new Date().toISOString(),
    summary: {
      totalChanges: classification.breaking.length + classification.additive.length + 
                   classification.docsOnly.length + classification.refactor.length,
      breakingCount: classification.breaking.length,
      additiveCount: classification.additive.length,
      docsOnlyCount: classification.docsOnly.length,
      refactorCount: classification.refactor.length
    }
  };
  
  // Write report to file
  fs.writeFileSync(outputPath, JSON.stringify(report, null, 2));
  
  return report;
}

function calculateVersionBump(classification: ChangeClassification, currentVersion: string): VersionInfo {
  let requiredBump: 'major' | 'minor' | 'patch' | 'none' = 'none';
  
  // Determine required version bump based on change types
  if (classification.breaking.length > 0) {
    requiredBump = 'major';
  } else if (classification.additive.length > 0) {
    requiredBump = 'minor';
  } else if (classification.docsOnly.length > 0) {
    requiredBump = 'patch';
  }
  
  const suggestedNew = bumpVersion(currentVersion, requiredBump);
  
  return {
    current: currentVersion,
    requiredBump,
    suggestedNew
  };
}

function bumpVersion(version: string, bumpType: 'major' | 'minor' | 'patch' | 'none'): string {
  if (bumpType === 'none') {
    return version;
  }
  
  const [major, minor, patch] = version.split('.').map(Number);
  
  switch (bumpType) {
    case 'major':
      return `${major + 1}.0.0`;
    case 'minor':
      return `${major}.${minor + 1}.0`;
    case 'patch':
      return `${major}.${minor}.${patch + 1}`;
    default:
      return version;
  }
}

export function loadCurrentVersion(versionFilePath: string = 'schemas/openapi/version.json'): string {
  try {
    const versionData = JSON.parse(fs.readFileSync(versionFilePath, 'utf8'));
    return versionData.apiVersion || '1.0.0';
  } catch (error) {
    console.warn(`Failed to load version from ${versionFilePath}, defaulting to 1.0.0:`, error);
    return '1.0.0';
  }
}

export function updateVersionFile(newVersion: string, versionFilePath: string = 'schemas/openapi/version.json', notes: string = ''): void {
  const versionData = {
    apiVersion: newVersion,
    updated: new Date().toISOString(),
    notes: notes || `Version bump to ${newVersion}`
  };
  
  fs.writeFileSync(versionFilePath, JSON.stringify(versionData, null, 2));
}