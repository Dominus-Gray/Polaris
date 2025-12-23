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
exports.diffSchemas = diffSchemas;
const _ = __importStar(require("lodash"));
function diffSchemas(oldSchemas, newSchemas) {
    const changes = [];
    // Create maps for easier lookup
    const oldMap = new Map(oldSchemas.map(s => [s.path, s]));
    const newMap = new Map(newSchemas.map(s => [s.path, s]));
    // Find removed schemas
    for (const [path, oldSchema] of oldMap) {
        if (!newMap.has(path)) {
            changes.push({
                type: 'remove',
                path: [path],
                oldValue: oldSchema.content,
                classificationHint: 'schema_removed'
            });
        }
    }
    // Find added schemas
    for (const [path, newSchema] of newMap) {
        if (!oldMap.has(path)) {
            changes.push({
                type: 'add',
                path: [path],
                newValue: newSchema.content,
                classificationHint: 'schema_added'
            });
        }
    }
    // Find modified schemas
    for (const [path, newSchema] of newMap) {
        const oldSchema = oldMap.get(path);
        if (oldSchema) {
            const schemaChanges = compareObjects(oldSchema.content, newSchema.content, [path]);
            changes.push(...schemaChanges);
        }
    }
    return changes;
}
function compareObjects(oldObj, newObj, basePath) {
    const changes = [];
    if (_.isEqual(oldObj, newObj)) {
        return changes;
    }
    // Handle primitive types
    if (!_.isObject(oldObj) || !_.isObject(newObj)) {
        changes.push({
            type: 'modify',
            path: basePath,
            oldValue: oldObj,
            newValue: newObj,
            classificationHint: 'value_changed'
        });
        return changes;
    }
    // Handle arrays
    if (Array.isArray(oldObj) || Array.isArray(newObj)) {
        if (!Array.isArray(oldObj) || !Array.isArray(newObj)) {
            changes.push({
                type: 'modify',
                path: basePath,
                oldValue: oldObj,
                newValue: newObj,
                classificationHint: 'type_changed'
            });
        }
        else {
            const arrayChanges = compareArrays(oldObj, newObj, basePath);
            changes.push(...arrayChanges);
        }
        return changes;
    }
    // Handle objects
    const oldKeys = new Set(Object.keys(oldObj));
    const newKeys = new Set(Object.keys(newObj));
    // Find removed keys
    for (const key of oldKeys) {
        if (!newKeys.has(key)) {
            changes.push({
                type: 'remove',
                path: [...basePath, key],
                oldValue: oldObj[key],
                classificationHint: getRemovalClassificationHint(basePath, key, oldObj[key])
            });
        }
    }
    // Find added keys
    for (const key of newKeys) {
        if (!oldKeys.has(key)) {
            changes.push({
                type: 'add',
                path: [...basePath, key],
                newValue: newObj[key],
                classificationHint: getAdditionClassificationHint(basePath, key, newObj[key])
            });
        }
    }
    // Find modified keys
    for (const key of newKeys) {
        if (oldKeys.has(key)) {
            const nestedChanges = compareObjects(oldObj[key], newObj[key], [...basePath, key]);
            changes.push(...nestedChanges);
        }
    }
    return changes;
}
function compareArrays(oldArray, newArray, basePath) {
    const changes = [];
    // Simple array comparison - detect additions/removals
    if (oldArray.length !== newArray.length) {
        changes.push({
            type: 'modify',
            path: basePath,
            oldValue: oldArray,
            newValue: newArray,
            classificationHint: 'array_length_changed'
        });
    }
    // Compare each element
    const maxLength = Math.max(oldArray.length, newArray.length);
    for (let i = 0; i < maxLength; i++) {
        const oldItem = i < oldArray.length ? oldArray[i] : undefined;
        const newItem = i < newArray.length ? newArray[i] : undefined;
        if (oldItem === undefined) {
            changes.push({
                type: 'add',
                path: [...basePath, i.toString()],
                newValue: newItem,
                classificationHint: 'array_item_added'
            });
        }
        else if (newItem === undefined) {
            changes.push({
                type: 'remove',
                path: [...basePath, i.toString()],
                oldValue: oldItem,
                classificationHint: 'array_item_removed'
            });
        }
        else if (!_.isEqual(oldItem, newItem)) {
            const itemChanges = compareObjects(oldItem, newItem, [...basePath, i.toString()]);
            changes.push(...itemChanges);
        }
    }
    return changes;
}
function getRemovalClassificationHint(basePath, key, value) {
    const pathStr = [...basePath, key].join('.');
    // Check for OpenAPI specific removals
    if (pathStr.includes('paths.') && pathStr.includes('.responses.')) {
        return 'response_removed';
    }
    if (pathStr.includes('paths.') && (key === 'get' || key === 'post' || key === 'put' || key === 'delete' || key === 'patch')) {
        return 'endpoint_removed';
    }
    if (pathStr.includes('required') || key === 'required') {
        return 'required_field_removed';
    }
    if (pathStr.includes('properties.')) {
        return 'property_removed';
    }
    return 'field_removed';
}
function getAdditionClassificationHint(basePath, key, value) {
    const pathStr = [...basePath, key].join('.');
    // Check for OpenAPI specific additions
    if (pathStr.includes('paths.') && pathStr.includes('.responses.')) {
        return 'response_added';
    }
    if (pathStr.includes('paths.') && (key === 'get' || key === 'post' || key === 'put' || key === 'delete' || key === 'patch')) {
        return 'endpoint_added';
    }
    if (pathStr.includes('required') || key === 'required') {
        return 'required_field_added';
    }
    if (pathStr.includes('properties.')) {
        return 'property_added';
    }
    return 'field_added';
}
