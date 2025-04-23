import { createMachine, assign, fromPromise } from 'xstate';
import { Notification } from './schema';
import { dispatchToOutputs } from '../outputs/index';

interface Context {
  raw: Notification;
  notification?: Notification;
  error?: string;
}

export const notificationMachine = createMachine({
  id: 'notification',
  types: {
    context: {} as Context,
    input: {} as { raw: Notification },
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
        src: fromPromise(({ input }) => {
          const raw = input.raw;
          const transformed: Notification = {
            source: raw.source || 'http',
            receivedAt: new Date().toISOString(),
            from: raw.from,
            to: raw.to,
            subject: raw.subject,
            body: raw.body,
            attachments: raw.attachments || [],
            meta: raw.meta || {},
          };
          return Promise.resolve(transformed);
        }),
        onDone: {
          target: 'dispatching',
          actions: assign({ notification: ({ event }) => event.output })
        },
        onError: {
          target: 'failed',
          actions: assign({ error: ({ event }) => (event.error as Error).message })
        }
      }
    },
    dispatching: {
      type: 'atomic',
      invoke: {
        src: fromPromise(({ input }) => dispatchToOutputs(input.raw))
      },
      onDone: 'success',
    },
    success: {
      type: 'final'
    },
    failed: {
      type: 'final'
    }
  }
});
