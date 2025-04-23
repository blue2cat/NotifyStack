import { createActor } from 'xstate';
import { notificationMachine } from './notificationMachine';
import { Notification } from './schema';

export async function processNotification(raw: Notification): Promise<void> {
  return new Promise((resolve, reject) => {
    const actor = createActor(notificationMachine, {
      input: { raw } // ✅ correct shape
    });

    actor.subscribe((state) => {
      console.log(`State: ${state.value}`);
      if (state.matches('success')) {
        resolve();
      } else if (state.matches('failed')) {
        reject(new Error(`Notification processing failed: ${state.context?.error}`));
      }
    });

    actor.start();
  });
}
