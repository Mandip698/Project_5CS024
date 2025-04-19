document.addEventListener("DOMContentLoaded", function () {
    const voteButton = document.getElementById("vote-button");
    const votingForm = document.getElementById("voting-form");
    const resultsContainer = document.getElementById("results-container");
    const totalVotesElement = document.getElementById("total-votes");
    const radioButtons = document.querySelectorAll('input[name="poll-option"]');
    const ctx = document.getElementById("results-chart").getContext("2d");

    let resultsChart = new Chart(ctx, {
        type: "pie",
        data: {
            labels: pollData.options.map((opt) => opt.name),
            datasets: [
                {
                    data: pollData.options.map((opt) => opt.votes),
                    backgroundColor: pollData.options.map((opt) => opt.color),
                    borderColor: "white",
                    borderWidth: 2,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: "bottom",
                    labels: { font: { size: 12 }, padding: 20 },
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            const value = context.raw || 0;
                            const total = context.chart.data.datasets[0].data.reduce((a, b) => a + b, 0);
                            const percent = total ? Math.round((value / total) * 100) : 0;
                            return `${context.label}: ${value} votes (${percent}%)`;
                        },
                    },
                },
            },
        },
    });

    updateTotalVotes();
    radioButtons.forEach((radio) => {
        radio.addEventListener("change", () => (voteButton.disabled = false));
    });

    voteButton.addEventListener("click", function (e) {
        e.preventDefault();
        const selected = document.querySelector('input[name="poll-option"]:checked');
        if (!selected) return;

        const optionId = parseInt(selected.value);
        const pollId = pollData.poll_id || window.location.pathname.split("/")[2];

        fetch("/poll/vote/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(),
            },
            body: JSON.stringify({
                poll_id: pollId,
                option_id: optionId,
            }),
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.error) {
                    toastr.error(data.error);
                    return;
                }
                const votedOption = pollData.options.find((opt) => opt.id === data.option_id);
                if (votedOption) votedOption.votes = data.votes;

                voteButton.disabled = true;
                radioButtons.forEach((radio) => (radio.disabled = true));
                toastr.success("Thank you for voting! Here are the current results.");
                updateChart();
                showResults();
            })
            .catch((err) => {
                toastr.error("Vote failed.");
                console.error("Vote failed:", err);
            });
    });

    function showResults() {
        votingForm.style.display = "none";
        resultsContainer.style.display = "block";
        resultsContainer.innerHTML = "";

        const totalVotes = pollData.options.reduce((sum, opt) => sum + opt.votes, 0);

        pollData.options.forEach((option) => {
            const percentage = totalVotes ? Math.round((option.votes / totalVotes) * 100) : 0;
            const bar = document.createElement("div");
            bar.className = "result-bar";
            bar.innerHTML = `
                <div class="result-info">
                    <span class="result-name">${option.name}</span>
                    <span class="result-votes">${option.votes} votes (${percentage}%)</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${percentage}%; background-color: ${option.color};"></div>
                </div>
            `;
            resultsContainer.appendChild(bar);
        });
        updateTotalVotes();
    }

    function updateChart() {
        resultsChart.data.datasets[0].data = pollData.options.map((opt) => opt.votes);
        resultsChart.update();
    }

    function updateTotalVotes() {
        const totalVotes = pollData.options.reduce((sum, option) => sum + option.votes, 0);
        totalVotesElement.textContent = `Total votes: ${totalVotes}`;
    }

    function getCSRFToken() {
        const cookie = document.cookie.split("; ").find((row) => row.startsWith("csrftoken="));
        return cookie ? cookie.split("=")[1] : "";
    }

    if (pollData.user_voted) {
        showResults();
    }
});
