import { RedisStore } from "rate-limit-redis";
import { Redis } from "ioredis";

const redisClient = new Redis({
    host: process.env.REDIS_HOST,
    port: Number(process.env.REDIS_PORT),
    password: process.env.REDIS_PASSWORD,
});

export function createRedisStore(prefix: string) {
    return new RedisStore({
        prefix,
        // @ts-expect-error
        sendCommand: (...args: string[]) =>
            redisClient.call(args[0], ...args.slice(1)),
    });
}