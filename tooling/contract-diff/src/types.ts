export interface SchemaFile {
  path: string;
  content: any;
  type: 'openapi' | 'event';
}

export interface SchemaChange {
  type: 'add' | 'remove' | 'modify';
  path: string[];
  oldValue?: any;
  newValue?: any;
  classificationHint?: string;
}

export interface ChangeClassification {
  breaking: SchemaChange[];
  additive: SchemaChange[];
  docsOnly: SchemaChange[];
  refactor: SchemaChange[];
}

export interface VersionInfo {
  current: string;
  requiredBump: 'major' | 'minor' | 'patch' | 'none';
  suggestedNew: string;
}

export interface DiffReport {
  breaking: SchemaChange[];
  additive: SchemaChange[];
  docsOnly: SchemaChange[];
  refactor: SchemaChange[];
  version: VersionInfo;
  timestamp: string;
  summary: {
    totalChanges: number;
    breakingCount: number;
    additiveCount: number;
    docsOnlyCount: number;
    refactorCount: number;
  };
}

export interface Config {
  docsOnlyPatterns: string[];
  ignoreOrdering: boolean;
  deprecationFields: string[];
  deprecationWindowDays: number;
  enforcement: 'warn' | 'block';
}

export interface DeprecationOverride {
  issueNumber: string;
  reason: string;
  impactedPaths: string[];
  approver: string;
  expiresAt?: string;
}