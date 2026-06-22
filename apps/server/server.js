import connectDB from "./src/config/database.js";
import app from "./src/app.js";
import http from "http";
import { initWebSocket } from "./src/utils/websocket.js";

connectDB();

const server = http.createServer(app);
initWebSocket(server);

server.listen(3000, () => {
  console.log("Server is running on port 3000");
});
