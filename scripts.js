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
                    newReview.id = `review-${stockName}`;
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
    fetch('https://api.github.com/repos/photo2story/buddy4/contents/')
        .then(response => response.json())
        .then(data => {
            const mplFile = data.find(file => file.name === `result_mpl_${stockName}.png`);
            if (mplFile) {
                const url = mplFile.download_url;
                window.open(url, '_blank');
            } else {
                alert('MPL chart not found.');
            }
        })
        .catch(error => console.error('Error fetching MPL chart:', error));
}

function addReview() {
    const stockName = document.getElementById('stockName').value.toUpperCase();
    console.log(`Stock name entered: ${stockName}`); // 디버깅 메시지 추가
    if (stockName) {
        fetch('https://api.github.com/repos/photo2story/buddy4/contents/')
            .then(response => response.json())
            .then(data => {
                const found = data.some(file => file.name.toUpperCase().includes(stockName));
                if (found) {
                    loadReviews();
                    scrollToReview(stockName);
                } else {
                    saveToSearchHistory(stockName);
                    alert('Review is being prepared. Please check back later.');
                }
            })
            .catch(error => console.error('Error fetching the file list:', error));
    } else {
        alert('Please enter a stock name.');
    }
}

function scrollToReview(stockName) {
    const reviewElement = document.getElementById(`review-${stockName}`);
    if (reviewElement) {
        reviewElement.scrollIntoView({ behavior: 'smooth' });
    } else {
        console.log(`Review for ${stockName} not found.`);
    }
}

function saveToSearchHistory(stockName) {
    // 여기에 search history.log에 저장하는 코드를 추가하세요.
    console.log(`Saving ${stockName} to search history.`);
}

document.getElementById('addReviewButton').addEventListener('click', addReview);

