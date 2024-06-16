// scripts.js

$(function() {
    loadReviews();

    const stockInput = $('#stockName');
    const suggestionsBox = $('#autocomplete-list');

    stockInput.autocomplete({
        source: function(request, response) {
            $.ajax({
                url: "http://localhost:8080/api/get_tickers",
                method: "GET",
                dataType: "json",
                success: function(data) {
                    console.log("Fetched tickers data: ", data); // Fetch된 데이터 출력
                    var filteredData = $.map(data, function(item) {
                        if (item.Symbol.toUpperCase().includes(request.term.toUpperCase()) ||
                            item.Name.toUpperCase().includes(request.term.toUpperCase())) {
                            return {
                                label: item.Symbol + " - " + item.Name + " - " + item.Market + " - " + item.Sector + " - " + item.Industry,
                                value: item.Symbol
                            };
                        } else {
                            return null;
                        }
                    });
                    console.log("Filtered data: ", filteredData); // 필터링된 데이터 출력
                    response(filteredData);
                },
                error: function(xhr, status, error) {
                    console.error("Error fetching tickers: ", error); // 에러 메시지 출력
                }
            });
        },
        select: function(event, ui) {
            stockInput.val(ui.item.value);
            console.log("선택된 티커: ", ui.item.value); // 선택된 티커 출력
            setTimeout(() => {
                $('#searchReviewButton').click();  // 선택과 동시에 검색
            }, 100);
            return false;
        }
    });

    stockInput.blur(function() {
        setTimeout(() => { suggestionsBox.html(''); }, 100);
    });

    $('#searchReviewButton').click(function() {
        const stockName = stockInput.val().toUpperCase();
        console.log("검색 버튼 클릭 후 stockName: ", stockName); // 검색 버튼 클릭 후 티커 출력
        const reviewList = $('#reviewList');
        const reviewItems = reviewList.find('.review');
        let stockFound = false;

        reviewItems.each(function() {
            const reviewItem = $(this);
            if (reviewItem.find('h3').text().includes(stockName)) {
                reviewItem[0].scrollIntoView({ behavior: 'smooth' });
                stockFound = true;
                return false;
            }
        });

        if (!stockFound) {
            saveToSearchHistory(stockName);
            alert('Review is being prepared. Please try again later.');
        }
    });
});

function loadReviews() {
    const reviewList = $('#reviewList');

    $.ajax({
        url: 'https://api.github.com/repos/photo2story/buddy4/contents/',
        method: 'GET',
        success: function(data) {
            data.forEach(file => {
                if (file.name.startsWith('comparison_') && file.name.endsWith('.png')) {
                    const stockName = file.name.replace('comparison_', '').replace('_VOO.png', '').toUpperCase();
                    const newReview = $('<div>').addClass('review').html(`
                        <h3>${stockName} vs VOO</h3>
                        <img src="${file.download_url}" alt="${stockName} vs VOO" style="width: 100%;" onclick="showMplChart('${stockName}')">
                    `);
                    reviewList.append(newReview);
                }
            });
        },
        error: function(xhr, status, error) {
            console.error('Error fetching the file list:', error); // 에러 메시지 출력
        }
    });
}

function showMplChart(stockName) {
    const url = `https://github.com/photo2story/buddy4/blob/main/result_mpl_${stockName}.png`;
    window.open(url, '_blank');
}

function saveToSearchHistory(stockName) {
    $.ajax({
        url: 'http://localhost:8080/save_search_history',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ stock_name: stockName }),
        success: function(data) {
            if (data.success) {
                console.log(`Saved ${stockName} to search history.`);
            } else {
                console.error('Failed to save to search history.');
            }
        },
        error: function(xhr, status, error) {
            console.error('Error saving to search history:', error); // 에러 메시지 출력
        }
    });
}

