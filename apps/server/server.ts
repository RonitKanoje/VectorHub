import connectDB from "./src/config/database.js";
import app from "./src/app.js";
import http from "http";
import { initWebSocket } from "./src/utils/websocket.js";
import config from "./src/config/config.js";

connectDB();

const server = http.createServer(app);
initWebSocket(server);

const port = Number(config.PORT);
server.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});
