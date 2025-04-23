// src/outputs/file.ts

import { Notification } from '../core/schema';
import fs from 'fs/promises';
import path from 'path';

export const fileOutput = {
  name: 'file',
  async handle(notification: Notification) {
    const outPath = path.resolve(__dirname, '../../logs/notifications.log');
    const entry = `[${new Date().toISOString()}]\n${JSON.stringify(notification, null, 2)}\n---\n`;
    await fs.mkdir(path.dirname(outPath), { recursive: true });
    await fs.appendFile(outPath, entry);
  }
};
