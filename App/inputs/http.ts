import express from 'express';
import logger from '../utils/logger';
import { validateNotification } from '../core/validate';
import { Notification } from '../core/schema';

import type { RequestHandler } from 'express';

export function startHttpListener(
  onNotification: (data: Notification) => Promise<void>,
  port = 3000
) {
  const app = express();

  app.use(express.json());



  const notifyHandler: RequestHandler = async (req, res) => {

    if (!req.body) {
      logger.warn('Empty notification payload received');
      res.status(400).json({ error: 'Empty notification payload' });
      return;
    }
    const raw = req.body;

    const { valid, errors } = validateNotification(raw);

    if (!valid) {
      res.status(400).json({
        error: 'Invalid notification input',
        details: errors
      });
      return;
    }

    const notification: Notification = {
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
    logger.info(`HTTP listener active on port ${port}`);
  });
}
