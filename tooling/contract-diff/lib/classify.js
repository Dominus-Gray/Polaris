"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.classify = classify;
exports.isDeprecatedRemoval = isDeprecatedRemoval;
const loadSchemas_1 = require("./loadSchemas");
function classify(changes) {
    const config = (0, loadSchemas_1.loadConfig)();
    const classification = {
        breaking: [],
        additive: [],
        docsOnly: [],
        refactor: []
    };
    for (const change of changes) {
        const category = classifyChange(change, config);
        classification[category].push(change);
    }
    return classification;
}
function classifyChange(change, config) {
    const pathStr = change.path.join('.');
    const lastSegment = change.path[change.path.length - 1];
    // Check if it's a docs-only change
    if (isDocsOnlyChange(change, config)) {
        return 'docsOnly';
    }
    // Check if it's a refactor/internal change
    if (isRefactorChange(change)) {
        return 'refactor';
    }
    // Breaking changes
    if (isBreakingChange(change)) {
        return 'breaking';
    }
    // Default to additive
    return 'additive';
}
function isDocsOnlyChange(change, config) {
    const lastSegment = change.path[change.path.length - 1];
    // Check if the field matches docs-only patterns
    return config.docsOnlyPatterns.some(pattern => lastSegment.toLowerCase().includes(pattern.toLowerCase()));
}
function isRefactorChange(change) {
    const pathStr = change.path.join('.');
    // Internal/implementation details that don't affect the contract
    const refactorPatterns = [
        'x-internal',
        'x-implementation',
        'x-private',
        'x-codegen'
    ];
    return refactorPatterns.some(pattern => pathStr.includes(pattern));
}
function isBreakingChange(change) {
    const pathStr = change.path.join('.');
    const hint = change.classificationHint || '';
    // Schema or endpoint removal is always breaking
    if (change.type === 'remove' && (hint === 'schema_removed' || hint === 'endpoint_removed')) {
        return true;
    }
    // Removing required fields is breaking
    if (change.type === 'remove' && hint === 'required_field_removed') {
        return true;
    }
    // Adding required fields is breaking
    if (change.type === 'add' && hint === 'required_field_added') {
        return true;
    }
    // Removing properties is breaking
    if (change.type === 'remove' && hint === 'property_removed') {
        return true;
    }
    // Removing response codes is breaking
    if (change.type === 'remove' && hint === 'response_removed') {
        return true;
    }
    // Type changes are typically breaking
    if (hint === 'type_changed') {
        return true;
    }
    // Check specific OpenAPI breaking patterns
    if (isOpenAPIBreakingChange(change, pathStr)) {
        return true;
    }
    // Check if it's making a field from optional to required
    if (isOptionalToRequiredChange(change, pathStr)) {
        return true;
    }
    return false;
}
function isOpenAPIBreakingChange(change, pathStr) {
    // OpenAPI specific breaking change patterns
    // Changing HTTP method
    if (pathStr.includes('paths.') && change.type === 'remove' &&
        ['get', 'post', 'put', 'delete', 'patch', 'options', 'head'].includes(change.path[change.path.length - 1])) {
        return true;
    }
    // Removing path parameters
    if (pathStr.includes('parameters') && change.type === 'remove' &&
        change.oldValue && change.oldValue.in === 'path') {
        return true;
    }
    // Changing parameter requirements
    if (pathStr.includes('parameters') && change.type === 'modify' &&
        change.oldValue?.required !== change.newValue?.required) {
        return true;
    }
    // Removing success response codes
    if (pathStr.includes('responses') && change.type === 'remove' &&
        /^2\d\d$/.test(change.path[change.path.length - 1])) {
        return true;
    }
    return false;
}
function isOptionalToRequiredChange(change, pathStr) {
    if (change.type !== 'modify') {
        return false;
    }
    // Check if a field changed from optional to required
    if (pathStr.includes('required') && change.oldValue === false && change.newValue === true) {
        return true;
    }
    // Check if a property was added to the required array
    if (pathStr.endsWith('required') && Array.isArray(change.newValue) && Array.isArray(change.oldValue)) {
        const addedRequired = change.newValue.filter((item) => !change.oldValue.includes(item));
        return addedRequired.length > 0;
    }
    return false;
}
function isDeprecatedRemoval(change, config) {
    if (change.type !== 'remove') {
        return false;
    }
    // Check if the removed field had deprecation metadata
    if (change.oldValue && typeof change.oldValue === 'object') {
        for (const depField of config.deprecationFields) {
            if (change.oldValue[depField]) {
                // Check if deprecation window has passed
                if (depField === 'x-sunset' && change.oldValue[depField]) {
                    const sunsetDate = new Date(change.oldValue[depField]);
                    const windowEnd = new Date(sunsetDate.getTime() + (config.deprecationWindowDays * 24 * 60 * 60 * 1000));
                    if (new Date() > windowEnd) {
                        return true; // Properly deprecated removal
                    }
                }
                else if (depField === 'x-status' && change.oldValue[depField] === 'deprecated') {
                    return true; // Marked as deprecated
                }
                else if (depField === 'deprecated' && change.oldValue[depField] === true) {
                    return true; // Standard OpenAPI deprecation
                }
            }
        }
    }
    return false;
}
