import mongoose from "mongoose";

const deviceSchema = new mongoose.Schema({
  deviceId: { type: String },
  latitude: { type: Number },
  longitude: { type: Number },
  temperature: { type: Number },
  max_temperature: { type: Number },
  humidity: { type: Number },
  pressure: { type: Number },
  uv_index: { type: Number },
});

const deviceModel = mongoose.model("Devices", deviceSchema);

export default deviceModel;
