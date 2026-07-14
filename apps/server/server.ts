import connectDB from "./src/config/database.js";
import app from "./src/app.js";
import http from "http";
import { initWebSocket } from "./src/utils/websocket.js";

connectDB();

const server = http.createServer(app);
initWebSocket(server);

const port = Number(process.env.PORT || 3000);
server.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});
