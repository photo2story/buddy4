const express = require('express');
const fs = require('fs');
const path = require('path');
const bodyParser = require('body-parser');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(bodyParser.json());

// Routes
app.post('/api/save_search_history', (req, res) => {
  const { stock_name } = req.body;

  if (!stock_name) {
    return res.status(400).json({ message: 'Stock name is required' });
  }

  const logFilePath = path.join(__dirname, 'search_history.log');
  const logEntry = `${new Date().toISOString()}: ${stock_name}\n`;

  fs.appendFile(logFilePath, logEntry, (err) => {
    if (err) {
      return res.status(500).json({ message: 'Failed to save search history' });
    }
    res.status(200).json({ success: true });
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
