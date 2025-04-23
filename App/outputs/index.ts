// src/outputs/index.ts

import { Notification } from '../core/schema';
import { fileOutput } from './file';

interface OutputModule {
  name: string;
  handle: (notification: Notification) => Promise<void>;
}

const enabledOutputs: OutputModule[] = [fileOutput];

export async function dispatchToOutputs(notification: Notification): Promise<void> {
  const failures: { name: string; reason: string }[] = [];

  await Promise.allSettled(
    enabledOutputs.map(async (output) => {
      try {
        await output.handle(notification);
        console.log(`Output [${output.name}] succeeded`);
      } catch (err: unknown) {
        console.error(`Output [${output.name}] failed`, err);
        const errorMessage = err instanceof Error ? err.message : 'unknown error';
        failures.push({ name: output.name, reason: errorMessage });
      }
    })
  );

  if (failures.length > 0) {
    const errorMsg = failures.map(f => `[${f.name}]: ${f.reason}`).join('; ');
    throw new Error(`Output failed: ${errorMsg}`);
  }
}
