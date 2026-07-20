import { RedisStore } from "rate-limit-redis";
import { Redis } from "ioredis"; // this is for redis client

const redisClient = new Redis({
    host: process.env.REDIS_HOST,
    port: Number(process.env.REDIS_PORT),
    password: process.env.REDIS_PASSWORD,
}); // create a new Redis client instance

export const redisStore = new RedisStore({
    // @ts-expect-error - Known type incompatibility between rate-limit-redis and ioredis
    sendCommand: (...args: string[]) => redisClient.call(args[0], ...args.slice(1)), // runs redis commands 
}); // for express-rate-limit creating the storage engine