"use strict";
// src/outputs/index.ts
Object.defineProperty(exports, "__esModule", { value: true });
exports.dispatchToOutputs = dispatchToOutputs;
const file_1 = require("./file");
const enabledOutputs = [file_1.fileOutput];
async function dispatchToOutputs(notification) {
    const failures = [];
    await Promise.allSettled(enabledOutputs.map(async (output) => {
        try {
            await output.handle(notification);
            console.log(`Output [${output.name}] succeeded`);
        }
        catch (err) {
            console.error(`Output [${output.name}] failed`, err);
            const errorMessage = err instanceof Error ? err.message : 'unknown error';
            failures.push({ name: output.name, reason: errorMessage });
        }
    }));
    if (failures.length > 0) {
        const errorMsg = failures.map(f => `[${f.name}]: ${f.reason}`).join('; ');
        throw new Error(`Output failed: ${errorMsg}`);
    }
}
//# sourceMappingURL=index.js.map