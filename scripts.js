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



