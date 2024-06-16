const express = require('express');
const bodyParser = require('body-parser');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 8080;

app.use(bodyParser.json());

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

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});

