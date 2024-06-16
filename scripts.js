// scripts.js

document.addEventListener('DOMContentLoaded', (event) => {
    loadReviews();

    const stockInput = document.getElementById('stockName');
    const suggestionsBox = document.getElementById('autocomplete-list');

    stockInput.addEventListener('input', function() {
        const query = this.value.toUpperCase();
        fetch('http://localhost:8080/api/get_tickers')
            .then(response => response.json())
            .then(data => {
                const suggestions = data.filter(item => item.Symbol.includes(query) || item.Name.toUpperCase().includes(query));
                suggestionsBox.innerHTML = '';
                suggestions.forEach(item => {
                    const suggestionItem = document.createElement('div');
                    suggestionItem.classList.add('autocomplete-suggestion');
                    suggestionItem.textContent = `${item.Symbol} - ${item.Name} - ${item.Market} - ${item.Sector} - ${item.Industry}`;
                    suggestionItem.addEventListener('click', () => {
                        stockInput.value = item.Symbol;  // 입력란에 선택된 티커만 남기기
                        suggestionsBox.innerHTML = '';
                        document.getElementById('searchReviewButton').click();  // 선택과 동시에 검색
                    });
                    suggestionsBox.appendChild(suggestionItem);
                });
            });
    });

    stockInput.addEventListener('blur', () => {
        setTimeout(() => { suggestionsBox.innerHTML = ''; }, 100);
    });

    document.getElementById('stockName').addEventListener('keyup', function(event) {
        if (event.key === 'Enter') {
            document.getElementById('searchReviewButton').click();
        }
    });

    document.getElementById('searchReviewButton').addEventListener('click', () => {
        const stockName = document.getElementById('stockName').value.toUpperCase();
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
            saveToSearchHistory(stockName);
            alert('Review is being prepared. Please try again later.');
        }
    });
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
    fetch('http://localhost:8080/save_search_history', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ stock_name: stockName }),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            console.log(`Saved ${stockName} to search history.`);
        } else {
            console.error('Failed to save to search history.');
        }
    })
    .catch(error => console.error('Error saving to search history:', error));
}





