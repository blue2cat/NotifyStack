"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.notificationMachine = void 0;
const xstate_1 = require("xstate");
const outputs_1 = require("../outputs");
exports.notificationMachine = (0, xstate_1.createMachine)({
    id: 'notification',
    types: {
        context: {},
        input: {},
    },
    context: ({ input }) => {
        console.log('FSM input received:', input);
        return {
            raw: input.raw,
            notification: undefined,
            error: undefined
        };
    },
    initial: 'transforming',
    states: {
        transforming: {
            type: 'atomic',
            invoke: {
                src: (0, xstate_1.fromPromise)(({ context }) => {
                    const raw = context.raw;
                    return Promise.resolve({
                        source: raw.source,
                        receivedAt: raw.receivedAt || new Date().toISOString(),
                        from: raw.from,
                        to: raw.to,
                        subject: raw.subject,
                        body: raw.body,
                        attachments: raw.attachments ?? [],
                        meta: raw.meta ?? {}
                    });
                }),
                onDone: {
                    target: 'dispatching',
                    actions: (0, xstate_1.assign)({ notification: ({ event }) => event.output })
                },
                onError: {
                    target: 'failed',
                    actions: (0, xstate_1.assign)({ error: ({ event }) => event.error.message })
                }
            }
        },
        dispatching: {
            type: 'atomic',
            invoke: {
                src: (0, xstate_1.fromPromise)(({ context }) => {
                    if (!context.notification) {
                        throw new Error('No notification to dispatch');
                    }
                    return (0, outputs_1.dispatchToOutputs)(context.notification);
                })
            },
            onDone: 'success',
            onError: {
                target: 'failed',
                actions: (0, xstate_1.assign)({ error: ({ event }) => event.error.message })
            }
        },
        success: { type: 'final' },
        failed: { type: 'final' }
    }
});
//# sourceMappingURL=notificationMachine.js.map