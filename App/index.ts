import { startHttpListener } from './inputs/http';
import logger from './utils/logger';
import { validateNotification } from './core/validate';
import { processNotification } from './core/stateMachine';

async function main() {
  try {
    logger.info('Starting Notification Gateway...');

    startHttpListener(async (rawData: unknown) => {
      const { valid, errors } = validateNotification(rawData);

      if (!valid) {
        logger.warn({ errors }, 'Invalid notification received');
        throw new Error('Invalid notification input');
      }

      const validated = rawData as Parameters<typeof processNotification>[0];

      try {
        await processNotification(validated);
        logger.info('Notification processed successfully');
      } catch (fsmErr) {
        logger.error({ fsmErr }, 'State machine failed to process notification');
        throw fsmErr;
      }
    });

    logger.info('System initialized. Ready to receive input.');
  } catch (err) {
    logger.fatal({ err }, 'Fatal error during startup');
    process.exit(1);
  }
}

main();
