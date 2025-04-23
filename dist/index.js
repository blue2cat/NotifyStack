"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const http_1 = require("./inputs/http");
const logger_1 = __importDefault(require("./utils/logger"));
const validate_1 = require("./core/validate");
const stateMachine_1 = require("./core/stateMachine");
async function main() {
    try {
        logger_1.default.info('Starting Notification Gateway...');
        (0, http_1.startHttpListener)(async (rawData) => {
            const { valid, errors } = (0, validate_1.validateNotification)(rawData);
            if (!valid) {
                logger_1.default.warn({ errors }, 'Invalid notification received');
                throw new Error('Invalid notification input');
            }
            const validated = rawData;
            try {
                await (0, stateMachine_1.processNotification)(validated);
                logger_1.default.info('Notification processed successfully');
            }
            catch (fsmErr) {
                logger_1.default.error({ fsmErr }, 'State machine failed to process notification');
                throw fsmErr;
            }
        });
        logger_1.default.info('System initialized. Ready to receive input.');
    }
    catch (err) {
        logger_1.default.fatal({ err }, 'Fatal error during startup');
        process.exit(1);
    }
}
main();
//# sourceMappingURL=index.js.map