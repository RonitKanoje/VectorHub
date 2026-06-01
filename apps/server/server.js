import connectDB from "./src/config/database.js";
import app from "./src/app.js";

connectDB();

app.listen(3000, () => {
  console.log("Server is running on port 3000");
});
