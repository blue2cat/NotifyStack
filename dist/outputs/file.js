"use strict";
// src/outputs/file.ts
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.fileOutput = void 0;
const promises_1 = __importDefault(require("fs/promises"));
const path_1 = __importDefault(require("path"));
exports.fileOutput = {
    name: 'file',
    async handle(notification) {
        const outPath = path_1.default.resolve(__dirname, '../../logs/notifications.log');
        const entry = `[${new Date().toISOString()}]\n${JSON.stringify(notification, null, 2)}\n---\n`;
        await promises_1.default.mkdir(path_1.default.dirname(outPath), { recursive: true });
        await promises_1.default.appendFile(outPath, entry);
    }
};
//# sourceMappingURL=file.js.map