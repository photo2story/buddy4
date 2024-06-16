// scripts.js

document.addEventListener('DOMContentLoaded', (event) => {
    loadReviews();

    const stockNameInput = document.getElementById('stockName');
    const searchReviewButton = document.getElementById('searchReviewButton');

    if (stockNameInput && searchReviewButton) {
        stockNameInput.addEventListener('keyup', function(event) {
            if (event.key === 'Enter') {
                searchReviewButton.click();
            }
        });

        searchReviewButton.addEventListener('click', () => {
            const stockName = stockNameInput.value.toUpperCase();
            const reviewList = document.getElementById('reviewList');
            const reviewItems = reviewList.getElementsByClassName('review');
            let stockFound = false;

            for (let i = 0; i < reviewItems.length; i++) {
                const reviewItem = reviewItems[i];
                if (reviewItem.querySelector('h3').innerText.includes(stockName)) {
                    reviewItem.scrollIntoView({ behavior: 'smooth' });
                    stockFound = true;
                    break;
                }
            }

            if (!stockFound) {
                alert('Review is being prepared, please try again later.');
                saveToSearchHistory(stockName);
            }
        });
    } else {
        console.error('Failed to find stockNameInput or searchReviewButton element.');
    }
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
                        <img src="${file.download_url}" alt="${stockName} vs VOO" style="width: 100%;" onclick="showMplChart('${stockName}')">
                    `;
                    reviewList.appendChild(newReview);
                }
            });
        })
        .catch(error => console.error('Error fetching the file list:', error));
}

function showMplChart(stockName) {
    const url = `https://github.com/photo2story/buddy4/blob/main/result_mpl_${stockName}.png`;
    window.open(url, '_blank');
}

function saveToSearchHistory(stockName) {
    fetch('/save_search_history', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ stock_name: stockName }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log(`Saved ${stockName} to search history.`);
        } else {
            console.error('Failed to save to search history.');
        }
    })
    .catch(error => console.error('Error saving to search history:', error));
}



