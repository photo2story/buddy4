// scripts.js

$(function() {
    loadReviews();

    const stockInput = $('#stockName');
    const suggestionsBox = $('#autocomplete-list');

    stockInput.on('input', function() {
        this.value = this.value.toUpperCase();
    });

    stockInput.autocomplete({
        source: function(request, response) {
            $.ajax({
                url: "http://localhost:8080/api/get_tickers",
                method: "GET",
                dataType: "json",
                success: function(data) {
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
                    response(filteredData);
                },
                error: function() {
                    console.error("Error fetching tickers");
                }
            });
        },
        select: function(event, ui) {
            stockInput.val(ui.item.value);
            $('#searchReviewButton').click();
            return false;
        }
    });

    stockInput.on('keypress', function(e) {
        if (e.which === 13) { // Enter key
            $('#searchReviewButton').click();
            return false;
        }
    });

    $('#searchReviewButton').click(function() {
        const stockName = stockInput.val().toUpperCase();
        const reviewList = $('#reviewList');
        const reviewItems = reviewList.find('.review');
        let stockFound = false;

        reviewItems.each(function() {
            const reviewItem = $(this);
            if (reviewItem.find('h3').text().includes(stockName)) {
                reviewItem[0].scrollIntoView({ behavior: 'smooth' });
                stockFound = true;
                return false; // break the loop
            }
        });

        if (!stockFound) {
            saveToSearchHistory(stockName);
            alert('Review is being prepared. Please try again later.');
        }
    });

    function loadReviews() {
        const reviewList = $('#reviewList');

        $.getJSON('https://api.github.com/repos/photo2story/buddy4/contents/', function(data) {
            $.each(data, function(index, file) {
                if (file.name.startsWith('comparison_') && file.name.endsWith('.png')) {
                    const stockName = file.name.replace('comparison_', '').replace('_VOO.png', '').toUpperCase();
                    const newReview = $('<div>', { class: 'review' });
                    newReview.html(`
                        <h3>${stockName} vs VOO</h3>
                        <img src="${file.download_url}" alt="${stockName} vs VOO" style="width: 100%;" onclick="showMplChart('${stockName}')">
                    `);
                    reviewList.append(newReview);
                }
            });
        }).fail(function() {
            console.error('Error fetching the file list');
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
            error: function() {
                console.error('Error saving to search history');
            }
        });
    }
});
