#!/usr/bin/env node
"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g = Object.create((typeof Iterator === "function" ? Iterator : Object).prototype);
    return g.next = verb(0), g["throw"] = verb(1), g["return"] = verb(2), typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (g && (g = 0, op[0] && (_ = 0)), _) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
Object.defineProperty(exports, "__esModule", { value: true });
var fs = require("fs");
var yaml = require("js-yaml");
var ContractLinter = /** @class */ (function () {
    function ContractLinter() {
        this.hasErrors = false;
        this.hasWarnings = false;
        this.config = {
            deprecationWindowDays: parseInt(process.env.DEPRECATION_WINDOW_DAYS || '90'),
            enforcementMode: (process.env.DIFF_ENFORCEMENT_MODE || 'warn'),
            overrideFilePath: process.env.OVERRIDE_FILE_PATH || '.deprecation-override.yml',
            versionFilePath: 'schemas/openapi/version.json'
        };
    }
    ContractLinter.prototype.enforceRules = function (reportPath) {
        return __awaiter(this, void 0, void 0, function () {
            var report, overrides, error_1;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        console.log('🔍 Contract Linter - Enforcing governance rules');
                        console.log("\uD83D\uDCCB Enforcement mode: ".concat(this.config.enforcementMode.toUpperCase()));
                        _a.label = 1;
                    case 1:
                        _a.trys.push([1, 5, , 6]);
                        report = this.loadReport(reportPath);
                        overrides = this.loadOverrides();
                        // Run enforcement checks
                        return [4 /*yield*/, this.checkVersionBumpRules(report)];
                    case 2:
                        // Run enforcement checks
                        _a.sent();
                        return [4 /*yield*/, this.checkDeprecationRules(report, overrides)];
                    case 3:
                        _a.sent();
                        return [4 /*yield*/, this.checkBreakingChangeRules(report, overrides)];
                    case 4:
                        _a.sent();
                        // Print summary and exit appropriately
                        this.printSummary();
                        this.exit();
                        return [3 /*break*/, 6];
                    case 5:
                        error_1 = _a.sent();
                        this.error('Failed to run contract linter:', error_1);
                        process.exit(1);
                        return [3 /*break*/, 6];
                    case 6: return [2 /*return*/];
                }
            });
        });
    };
    ContractLinter.prototype.loadReport = function (reportPath) {
        if (!fs.existsSync(reportPath)) {
            throw new Error("Diff report not found: ".concat(reportPath));
        }
        var reportContent = fs.readFileSync(reportPath, 'utf8');
        return JSON.parse(reportContent);
    };
    ContractLinter.prototype.loadOverrides = function () {
        if (!fs.existsSync(this.config.overrideFilePath)) {
            return [];
        }
        try {
            var overrideContent = fs.readFileSync(this.config.overrideFilePath, 'utf8');
            var parsed = yaml.load(overrideContent);
            return Array.isArray(parsed.overrides) ? parsed.overrides : [];
        }
        catch (error) {
            this.warn("Failed to parse override file: ".concat(error));
            return [];
        }
    };
    ContractLinter.prototype.checkVersionBumpRules = function (report) {
        return __awaiter(this, void 0, void 0, function () {
            var currentFileVersion, versionData, requiredBump, currentVersion, suggestedVersion, message;
            return __generator(this, function (_a) {
                console.log('\n📈 Checking version bump rules...');
                currentFileVersion = '1.0.0';
                try {
                    if (fs.existsSync(this.config.versionFilePath)) {
                        versionData = JSON.parse(fs.readFileSync(this.config.versionFilePath, 'utf8'));
                        currentFileVersion = versionData.apiVersion || '1.0.0';
                    }
                }
                catch (error) {
                    this.warn("Failed to load version file: ".concat(error));
                }
                requiredBump = report.version.requiredBump;
                currentVersion = report.version.current;
                suggestedVersion = report.version.suggestedNew;
                if (currentFileVersion !== currentVersion) {
                    this.warn("Version file mismatch: file shows ".concat(currentFileVersion, ", report shows ").concat(currentVersion));
                }
                if (requiredBump !== 'none') {
                    message = "Changes require ".concat(requiredBump, " version bump (").concat(currentVersion, " \u2192 ").concat(suggestedVersion, ")");
                    if (this.config.enforcementMode === 'block') {
                        this.error(message);
                    }
                    else {
                        this.warn(message);
                    }
                }
                else {
                    this.success('No version bump required');
                }
                return [2 /*return*/];
            });
        });
    };
    ContractLinter.prototype.checkDeprecationRules = function (report, overrides) {
        return __awaiter(this, void 0, void 0, function () {
            var removals, _i, removals_1, removal, path_1, hasOverride, wasDeprecated, message;
            return __generator(this, function (_a) {
                console.log('\\n⏰ Checking deprecation rules...');
                removals = report.breaking.filter(function (change) { return change.type === 'remove'; });
                if (removals.length === 0) {
                    this.success('No field/endpoint removals detected');
                    return [2 /*return*/];
                }
                for (_i = 0, removals_1 = removals; _i < removals_1.length; _i++) {
                    removal = removals_1[_i];
                    path_1 = removal.path.join('.');
                    hasOverride = this.checkOverrideForPath(path_1, overrides);
                    if (hasOverride) {
                        this.info("Removal of ".concat(path_1, " allowed by override"));
                        continue;
                    }
                    wasDeprecated = this.checkIfDeprecated(removal);
                    if (!wasDeprecated) {
                        message = "Removal of ".concat(path_1, " without proper deprecation (requires ").concat(this.config.deprecationWindowDays, " day deprecation period)");
                        if (this.config.enforcementMode === 'block') {
                            this.error(message);
                        }
                        else {
                            this.warn(message);
                        }
                    }
                    else {
                        this.success("Removal of ".concat(path_1, " follows deprecation policy"));
                    }
                }
                return [2 /*return*/];
            });
        });
    };
    ContractLinter.prototype.checkBreakingChangeRules = function (report, overrides) {
        return __awaiter(this, void 0, void 0, function () {
            var unapprovedBreaking, message;
            var _this = this;
            return __generator(this, function (_a) {
                console.log('\\n💥 Checking breaking change rules...');
                if (report.summary.breakingCount === 0) {
                    this.success('No breaking changes detected');
                    return [2 /*return*/];
                }
                unapprovedBreaking = report.breaking.filter(function (change) {
                    var path = change.path.join('.');
                    return !_this.checkOverrideForPath(path, overrides);
                });
                if (unapprovedBreaking.length > 0) {
                    message = "".concat(unapprovedBreaking.length, " unapproved breaking changes detected");
                    if (this.config.enforcementMode === 'block') {
                        this.error(message);
                        unapprovedBreaking.forEach(function (change, index) {
                            console.log("   ".concat(index + 1, ". ").concat(change.type.toUpperCase(), " ").concat(change.path.join('.')));
                        });
                    }
                    else {
                        this.warn(message);
                    }
                }
                else {
                    this.success('All breaking changes have valid overrides');
                }
                return [2 /*return*/];
            });
        });
    };
    ContractLinter.prototype.checkOverrideForPath = function (path, overrides) {
        return overrides.some(function (override) {
            // Check if any override covers this path
            return override.impactedPaths.some(function (overridePath) {
                return path.startsWith(overridePath) || overridePath === '*';
            });
        });
    };
    ContractLinter.prototype.checkIfDeprecated = function (removal) {
        // Check if the removed field had deprecation metadata
        if (removal.oldValue && typeof removal.oldValue === 'object') {
            return Boolean(removal.oldValue['x-status'] === 'deprecated' ||
                removal.oldValue['deprecated'] === true ||
                removal.oldValue['x-sunset']);
        }
        return false;
    };
    ContractLinter.prototype.success = function (message) {
        console.log("   \u2705 ".concat(message));
    };
    ContractLinter.prototype.info = function (message) {
        console.log("   \u2139\uFE0F  ".concat(message));
    };
    ContractLinter.prototype.warn = function (message) {
        console.log("   \u26A0\uFE0F  ".concat(message));
        this.hasWarnings = true;
    };
    ContractLinter.prototype.error = function (message, error) {
        console.log("   \u274C ".concat(message));
        if (error) {
            console.log("      ".concat(error));
        }
        this.hasErrors = true;
    };
    ContractLinter.prototype.printSummary = function () {
        console.log('\\n📊 Linter Summary:');
        if (this.hasErrors) {
            console.log('   ❌ Errors found - contract changes violate governance rules');
        }
        else if (this.hasWarnings) {
            console.log('   ⚠️  Warnings found - please review contract changes');
        }
        else {
            console.log('   ✅ All governance rules passed');
        }
    };
    ContractLinter.prototype.exit = function () {
        if (this.hasErrors && this.config.enforcementMode === 'block') {
            process.exit(1);
        }
        else {
            process.exit(0);
        }
    };
    return ContractLinter;
}());
// CLI execution
if (require.main === module) {
    var reportPath = process.argv[2] || 'contract-diff-report.json';
    var linter = new ContractLinter();
    linter.enforceRules(reportPath);
}
