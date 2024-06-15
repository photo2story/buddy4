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
    const reviewList = document.getElementById('reviewList');

    if (stockName) {
        const newReview = document.createElement('div');
        newReview.className = 'review';
        newReview.innerHTML = `
            <h3>${stockName} vs VOO</h3>
            <img src="https://raw.githubusercontent.com/photo2story/buddy4/main/comparison_${stockName}_VOO.png" alt="${stockName} vs VOO">
        `;
        reviewList.appendChild(newReview);
    } else {
        alert('Please enter a stock name.');
    }
}




