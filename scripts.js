document.addEventListener('DOMContentLoaded', (event) => {
    loadReviews();
});

function loadReviews() {
    const reviewList = document.getElementById('reviewList');

    fetch('https://api.github.com/repos/photo2story/buddy4/contents/')
        .then(response => response.json())
        .then(data => {
            data.forEach(file => {
                if (file.name.startsWith('comparison_') && file.name.endsWith('.png')) {
                    const stockName = file.name.replace('comparison_', '').replace('_VOO.png', '').toUpperCase();
                    const newReview = document.createElement('div');
                    newReview.className = 'review';
                    newReview.innerHTML = `
                        <h3>${stockName} vs VOO</h3>
                        <img src="${file.download_url}" alt="${stockName} vs VOO">
                    `;
                    reviewList.appendChild(newReview);
                }
            });
        })
        .catch(error => console.error('Error fetching the file list:', error));
}

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

document.getElementById('addReviewButton').addEventListener('click', addReview);
