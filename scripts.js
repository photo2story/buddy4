
function addReview() {
    const stockName = document.getElementById('stockName').value;
    if (stockName) {
        const reviewList = document.getElementById('reviewList');
        const newReview = document.createElement('div');
        newReview.className = 'review';
        newReview.innerHTML = `
            <h3>${stockName} vs VOO</h3>
            <canvas id="${stockName.toLowerCase()}VsVooChart"></canvas>
        `;
        reviewList.appendChild(newReview);
        // Here you can add code to actually draw the chart using a chart library like Chart.js
    }
}
