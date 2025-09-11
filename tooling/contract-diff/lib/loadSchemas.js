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
exports.loadSchemas = loadSchemas;
exports.loadConfig = loadConfig;
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
const yaml = __importStar(require("js-yaml"));
function loadSchemas(directory) {
    const schemas = [];
    function processDirectory(dir, baseDir = directory) {
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
            }
            else if (entry.isFile() && /\.(json|yaml|yml)$/i.test(entry.name) && !shouldSkipFile(entry.name, relativePath)) {
                try {
                    const content = fs.readFileSync(fullPath, 'utf8');
                    let parsedContent;
                    if (fullPath.endsWith('.json')) {
                        parsedContent = JSON.parse(content);
                    }
                    else {
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
                }
                catch (error) {
                    console.warn(`Failed to parse schema file ${fullPath}:`, error);
                }
            }
        }
    }
    processDirectory(directory);
    return schemas;
}
function shouldSkipDirectory(dirName, relativePath) {
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
    return skipPatterns.some(pattern => dirName === pattern || relativePath.includes(`${pattern}/`));
}
function shouldSkipFile(fileName, relativePath) {
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
function detectSchemaType(filePath, content) {
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
function normalizeSchema(schema) {
    if (schema === null || schema === undefined) {
        return schema;
    }
    if (Array.isArray(schema)) {
        return schema.map(normalizeSchema);
    }
    if (typeof schema === 'object') {
        const normalized = {};
        // Sort keys to ensure consistent ordering
        const sortedKeys = Object.keys(schema).sort();
        for (const key of sortedKeys) {
            normalized[key] = normalizeSchema(schema[key]);
        }
        return normalized;
    }
    return schema;
}
function loadConfig() {
    const configPath = path.join(__dirname, '..', 'config.json');
    try {
        const configContent = fs.readFileSync(configPath, 'utf8');
        return JSON.parse(configContent);
    }
    catch (error) {
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
