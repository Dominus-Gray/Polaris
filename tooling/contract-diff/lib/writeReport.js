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
exports.writeReport = writeReport;
exports.loadCurrentVersion = loadCurrentVersion;
exports.updateVersionFile = updateVersionFile;
const fs = __importStar(require("fs"));
function writeReport(classification, currentVersion, outputPath = 'contract-diff-report.json') {
    const versionInfo = calculateVersionBump(classification, currentVersion);
    const report = {
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
function calculateVersionBump(classification, currentVersion) {
    let requiredBump = 'none';
    // Determine required version bump based on change types
    if (classification.breaking.length > 0) {
        requiredBump = 'major';
    }
    else if (classification.additive.length > 0) {
        requiredBump = 'minor';
    }
    else if (classification.docsOnly.length > 0) {
        requiredBump = 'patch';
    }
    const suggestedNew = bumpVersion(currentVersion, requiredBump);
    return {
        current: currentVersion,
        requiredBump,
        suggestedNew
    };
}
function bumpVersion(version, bumpType) {
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
function loadCurrentVersion(versionFilePath = 'schemas/openapi/version.json') {
    try {
        const versionData = JSON.parse(fs.readFileSync(versionFilePath, 'utf8'));
        return versionData.apiVersion || '1.0.0';
    }
    catch (error) {
        console.warn(`Failed to load version from ${versionFilePath}, defaulting to 1.0.0:`, error);
        return '1.0.0';
    }
}
function updateVersionFile(newVersion, versionFilePath = 'schemas/openapi/version.json', notes = '') {
    const versionData = {
        apiVersion: newVersion,
        updated: new Date().toISOString(),
        notes: notes || `Version bump to ${newVersion}`
    };
    fs.writeFileSync(versionFilePath, JSON.stringify(versionData, null, 2));
}
