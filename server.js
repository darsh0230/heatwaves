import express from "express";
import dotenv from "dotenv";
import mongoose from "mongoose";
import cookieParser from "cookie-parser";
import cors from "cors";
import morgan from "morgan";
import "express-async-errors";

import errorHandlerMiddleware from "./middlewares/error-handler.js";
import notFoundMiddleware from "./middlewares/not-found.js";
import verifyJWT from "./middlewares/verifyJWT.js";
import credentials from "./middlewares/credentials.js";
import corsOptions from "./config/corsOptions.js";

import userRoutes from "./routes/userRoutes.js";

import Device from "./model/deviceModel.js";

dotenv.config();

const app = express();

//middleware

app.use(credentials);

app.use(cors());

app.use(express.json({ limit: "30mb", extended: true }));
app.use(express.urlencoded({ limit: "30mb", extended: true }));
app.use(cookieParser());

app.use(morgan("dev"));

const baseUrl = "/api/v1";

app.use(`${baseUrl}/users`, userRoutes);

//test endpoint
app.get("/", (req, res) => {
  res.status(200).json({ message: "hello" });
});

app.get(`${baseUrl}/getDevDetails`, async (req, res) => {
  const devDetails = await Device.find();
  res.status(200).json({ result: devDetails });
});

app.use(verifyJWT);
// protected routes should come after this line

app.use(errorHandlerMiddleware);
app.use(notFoundMiddleware);

const PORT = process.env.PORT || 5000;

mongoose
  .connect(process.env.MONGO_URI)
  .then(() =>
    app.listen(PORT, () => console.log(`Server running on port ${PORT}`))
  )
  .catch((error) => console.log(error.message));
