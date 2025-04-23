"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.startHttpListener = startHttpListener;
const express_1 = __importDefault(require("express"));
const logger_1 = __importDefault(require("../utils/logger"));
const validate_1 = require("../core/validate");
function startHttpListener(onNotification, port = 3000) {
    const app = (0, express_1.default)();
    app.use(express_1.default.json());
    const notifyHandler = async (req, res) => {
        if (!req.body) {
            logger_1.default.warn('Empty notification payload received');
            res.status(400).json({ error: 'Empty notification payload' });
            return;
        }
        const raw = req.body;
        const { valid, errors } = (0, validate_1.validateNotification)(raw);
        if (!valid) {
            res.status(400).json({
                error: 'Invalid notification input',
                details: errors
            });
            return;
        }
        const notification = {
            ...raw,
            receivedAt: raw.receivedAt || new Date().toISOString()
        };
        await onNotification(notification);
        res.status(200).json({ message: '✅ Notification accepted' });
    };
    app.post('/notify', notifyHandler);
    app.get('/healthz', (_req, res) => {
        res.status(200).json({ status: 'ok' });
    });
    app.listen(port, () => {
        logger_1.default.info(`HTTP listener active on port ${port}`);
    });
}
//# sourceMappingURL=http.js.map