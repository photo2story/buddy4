// scripts.js

$(function() {
    let currentPage = 1; // 현재 페이지 초기화
    const perPage = 100; // 페이지당 항목 수 설정
    loadReviews();

    const stockInput = $('#stockName');
    const suggestionsBox = $('#autocomplete-list');

    stockInput.autocomplete({
        source: function(request, response) {
            $.ajax({
                url: `http://localhost:8080/api/get_tickers?page=${currentPage}&per_page=${perPage}`,
                method: "GET",
                dataType: "json",
                success: function(data) {
                    console.log("Fetched tickers data: ", data); // Fetch된 데이터 출력
                    var filteredData = $.map(data, function(item) {
                        if (item.Symbol && item.Name) {
                            if (item.Symbol.toUpperCase().includes(request.term.toUpperCase()) ||
                                item.Name.toUpperCase().includes(request.term.toUpperCase())) {
                                return {
                                    label: item.Symbol + " - " + item.Name + " - " + item.Market + " - " + item.Sector + " - " + item.Industry,
                                    value: item.Symbol
                                };
                            }
                        }
                        return null;
                    }).filter(item => item !== null); // null 항목 제거
                    console.log("Filtered data: ", filteredData); // 필터링된 데이터 출력
                    response(filteredData);

                    if (filteredData.length < perPage) {
                        currentPage++; // 페이지 증가
                    }
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
    const reviewItems = reviewList.find('.review');
    let stockFound = false;

    reviewItems.each(function() {
        const reviewItem = $(this);
        if (reviewItem.find('h3').text().includes(stockName)) {
            reviewItem[0].scrollIntoView({ behavior: 'smooth' });
            stockFound = true;
            return false; // break out of each loop
        }
    });

    if (!stockFound) {
        saveToSearchHistory(stockName);
        alert('Review is being prepared. Please try again later.');
    }
});
