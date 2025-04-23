import pino from 'pino';

const isDev = process.env.NODE_ENV !== 'production';

const logger = pino({
  transport: isDev
    ? {
        target: 'pino-pretty',
        options: {
          colorize: true,
          translateTime: 'SYS:standard',
          ignore: 'pid,hostname'
        }
      }
    : undefined
});

export default logger;
