declare global {
  namespace Express {
    interface Request {
      userId?: string;
      xhr?: boolean; // returns true if request was issued with "X-Requested-With: XMLHttpRequest" header
    }
  }
}

export {};
