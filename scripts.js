function addReview() {
    const stockName = document.getElementById('stockName').value.toUpperCase();
    if (stockName) {
        fetch('/execute_stock_command', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ stock_name: stockName }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(`Stock ${stockName} review is being processed.`);
            } else {
                alert(`Failed to add review for stock ${stockName}.`);
            }
        })
        .catch(error => console.error('Error executing stock command:', error));
    } else {
        alert('Please enter a stock name.');
    }
}





