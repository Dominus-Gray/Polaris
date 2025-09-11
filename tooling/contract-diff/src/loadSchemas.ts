import * as fs from 'fs';
import * as path from 'path';
import * as yaml from 'js-yaml';
import { SchemaFile } from './types';

export function loadSchemas(directory: string): SchemaFile[] {
  const schemas: SchemaFile[] = [];
  
  function processDirectory(dir: string, baseDir: string = directory): void {
    if (!fs.existsSync(dir)) {
      return;
    }
    
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    
    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);
      const relativePath = path.relative(baseDir, fullPath);
      
      // Skip node_modules, .git, and other non-schema directories
      if (entry.isDirectory()) {
        if (!shouldSkipDirectory(entry.name, relativePath)) {
          processDirectory(fullPath, baseDir);
        }
      } else if (entry.isFile() && /\.(json|yaml|yml)$/i.test(entry.name) && !shouldSkipFile(entry.name, relativePath)) {
        try {
          const content = fs.readFileSync(fullPath, 'utf8');
          let parsedContent: any;
          
          if (fullPath.endsWith('.json')) {
            parsedContent = JSON.parse(content);
          } else {
            parsedContent = yaml.load(content);
          }
          
          // Normalize the schema by removing description-only fields if configured
          const normalizedContent = normalizeSchema(parsedContent);
          
          const schemaType = detectSchemaType(relativePath, normalizedContent);
          
          schemas.push({
            path: relativePath,
            content: normalizedContent,
            type: schemaType
          });
        } catch (error) {
          console.warn(`Failed to parse schema file ${fullPath}:`, error);
        }
      }
    }
  }
  
  processDirectory(directory);
  return schemas;
}

function shouldSkipDirectory(dirName: string, relativePath: string): boolean {
  const skipPatterns = [
    'node_modules',
    '.git',
    '.vscode',
    '.idea',
    'lib',
    'dist',
    'build',
    'coverage',
    '.next',
    'out'
  ];
  
  return skipPatterns.some(pattern => 
    dirName === pattern || relativePath.includes(`${pattern}/`)
  );
}

function shouldSkipFile(fileName: string, relativePath: string): boolean {
  const skipPatterns = [
    'package.json',
    'package-lock.json',
    'tsconfig.json',
    'jest.config.json',
    'eslint.config.json'
  ];
  
  // Skip files in tooling directories unless they're config files we want
  if (relativePath.includes('tooling/') && fileName !== 'config.json') {
    return true;
  }
  
  return skipPatterns.includes(fileName);
}

function detectSchemaType(filePath: string, content: any): 'openapi' | 'event' {
  // Check if it's an OpenAPI schema
  if (content.openapi || content.swagger || content.info || content.paths) {
    return 'openapi';
  }
  
  // Check if it's in events directory or has event-like structure
  if (filePath.includes('events/') || filePath.includes('event-')) {
    return 'event';
  }
  
  // Default to event schema
  return 'event';
}

function normalizeSchema(schema: any): any {
  if (schema === null || schema === undefined) {
    return schema;
  }
  
  if (Array.isArray(schema)) {
    return schema.map(normalizeSchema);
  }
  
  if (typeof schema === 'object') {
    const normalized: any = {};
    
    // Sort keys to ensure consistent ordering
    const sortedKeys = Object.keys(schema).sort();
    
    for (const key of sortedKeys) {
      normalized[key] = normalizeSchema(schema[key]);
    }
    
    return normalized;
  }
  
  return schema;
}

export function loadConfig(): any {
  const configPath = path.join(__dirname, '..', 'config.json');
  try {
    const configContent = fs.readFileSync(configPath, 'utf8');
    return JSON.parse(configContent);
  } catch (error) {
    console.warn('Failed to load config, using defaults:', error);
    return {
      docsOnlyPatterns: ['description', 'example', 'examples', 'summary', 'title'],
      ignoreOrdering: true,
      deprecationFields: ['x-status', 'x-sunset', 'deprecated'],
      deprecationWindowDays: 90,
      enforcement: 'warn'
    };
  }
}