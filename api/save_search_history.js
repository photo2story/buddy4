// api/save_search_history.js

const fs = require('fs');
const path = require('path');

module.exports = (req, res) => {
  if (req.method !== 'POST') {
    res.status(405).send({ message: 'Only POST requests are allowed' });
    return;
  }

  const { stock_name } = req.body;
  if (!stock_name) {
    res.status(400).send({ message: 'Stock name is required' });
    return;
  }

  const logFilePath = path.join(__dirname, '../../search_history.log');
  const logEntry = `${new Date().toISOString()}: ${stock_name}\n`;

  fs.appendFile(logFilePath, logEntry, (err) => {
    if (err) {
      res.status(500).send({ message: 'Failed to save search history' });
      return;
    }
    res.status(200).send({ success: true });
  });
};

