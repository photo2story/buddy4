// scripts.js

$(function() {
    loadReviews();

    const stockInput = $('#stockName');
    const suggestionsBox = $('#autocomplete-list');

    stockInput.autocomplete({
        source: function(request, response) {
            $.ajax({
                url: `http://localhost:8080/api/get_tickers`,
                method: "GET",
                dataType: "xml",
                success: function(data) {
                    console.log("Fetched tickers data: ", data); // Fetch된 데이터 출력
                    const items = $(data).find('item');
                    const filteredData = $.map(items, function(item) {
                        const symbol = $(item).find('Symbol').text();
                        const name = $(item).find('Name').text();
                        const market = $(item).find('Market').text();
                        const sector = $(item).find('Sector').text();
                        const industry = $(item).find('Industry').text();

                        if (symbol.toUpperCase().includes(request.term.toUpperCase()) ||
                            name.toUpperCase().includes(request.term.toUpperCase())) {
                            return {
                                label: symbol + " - " + name + " - " + market + " - " + sector + " - " + industry,
                                value: symbol
                            };
                        }
                        return null;
                    }).filter(item => item !== null); // null 항목 제거
                    console.log("Filtered data: ", filteredData); // 필터링된 데이터 출력
                    response(filteredData);
                },
                error: function(xhr, status, error) {
                    console.error("Error fetching tickers: ", error); // 에러 메시지 출력
                }
            });
        },
        select: function(event, ui) {
            console.log('선택된 항목:', ui.item.value); // 선택된 항목 출력
            stockInput.val(ui.item.value); // 선택된 값 입력란에 설정
            setTimeout(() => {
                $('#searchReviewButton').click(); // 선택과 동시에 검색
            }, 100);
        }
    });
});

function loadReviews() {
    const reviewList = document.getElementById('reviewList');

    fetch('https://api.github.com/repos/photo2story/buddy4/contents/')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
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

$('#searchReviewButton').on('click', () => {
    const stockName = $('#stockName').val().toUpperCase();
    const reviewList = $('#reviewList');
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
