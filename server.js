const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");
const app = express();

app.use(cors());
app.use(express.json());

// MongoDB connect
mongoose.connect("mongodb://127.0.0.1:27017/lottery");

// User Schema
const UserSchema = new mongoose.Schema({
  username: String,
  password: String,
  coins: { type: Number, default: 100 }
});

const User = mongoose.model("User", UserSchema);

// Ticket Schema
const TicketSchema = new mongoose.Schema({
  userId: String,
  number: Number
});

const Ticket = mongoose.model("Ticket", TicketSchema);

// Signup
app.post("/signup", async (req, res) => {
  const user = new User(req.body);
  await user.save();
  res.send("User created");
});

// Login
app.post("/login", async (req, res) => {
  const user = await User.findOne(req.body);
  if (!user) return res.send("Invalid");
  res.send(user);
});

// Buy Ticket
app.post("/buy", async (req, res) => {
  const { userId, number } = req.body;

  const user = await User.findById(userId);
  if (user.coins < 10) return res.send("Not enough coins");

  user.coins -= 10;
  await user.save();

  const ticket = new Ticket({ userId, number });
  await ticket.save();

  res.send("Ticket bought");
});

// Draw Winner
app.get("/draw", async (req, res) => {
  const tickets = await Ticket.find();
  if (tickets.length === 0) return res.send("No tickets");

  const winner = tickets[Math.floor(Math.random() * tickets.length)];

  await User.findByIdAndUpdate(winner.userId, {
    $inc: { coins: 100 }
  });

  await Ticket.deleteMany();

  res.send({ winner });
});

app.listen(3000, () => console.log("Server running 🚀"));
