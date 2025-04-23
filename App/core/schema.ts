export interface Attachment {
  filename: string;
  contentType: string;
  size: number;
  content: string;
}

export interface NotificationBody {
  text: string;
  html?: string;
}

export type NotificationSource = 'smtp' | 'http' | 'api';

export interface Notification {
  source: NotificationSource;
  receivedAt: string;
  from: string;
  to: string[];
  subject: string;
  body: NotificationBody;
  attachments: Attachment[];
  meta?: Record<string, unknown>;
}
