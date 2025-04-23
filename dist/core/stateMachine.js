"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.processNotification = processNotification;
const xstate_1 = require("xstate");
const notificationMachine_1 = require("./notificationMachine");
async function processNotification(raw) {
    return new Promise((resolve, reject) => {
        const actor = (0, xstate_1.createActor)(notificationMachine_1.notificationMachine, {
            input: { raw } // ✅ correct shape
        });
        actor.subscribe((state) => {
            console.log(`State: ${state.value}`);
            if (state.matches('success')) {
                resolve();
            }
            else if (state.matches('failed')) {
                reject(new Error(`Notification processing failed: ${state.context?.error}`));
            }
        });
        actor.start();
    });
}
//# sourceMappingURL=stateMachine.js.map