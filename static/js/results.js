document.addEventListener("DOMContentLoaded", () => {
  const options = [
    { id: 1, name: "Test", votes: 0 },
    { id: 2, name: "Test1", votes: 0 },
  ];

  const totalVotesEl = document.getElementById("total-votes");
  const progress1El = document.getElementById("progress-1");
  const progress2El = document.getElementById("progress-2");
  const percentage1El = document.getElementById("percentage-1");
  const percentage2El = document.getElementById("percentage-2");

  const ctx = document.getElementById("votesPieChart").getContext("2d");
  const pieChart = new Chart(ctx, {
    type: "pie",
    data: {
      labels: options.map(opt => opt.name),
      datasets: [{
        label: 'Votes',
        data: options.map(opt => opt.votes),
        backgroundColor: ["#4caf50", "#007BFF"],
        borderColor: "#fff",
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          position: 'bottom'
        }
      }
    }
  });

  function getTotalVotes() {
    return options.reduce((acc, opt) => acc + opt.votes, 0);
  }

  function updateUI() {
    const total = getTotalVotes();
    totalVotesEl.textContent = `Total votes: ${total}`;

    options.forEach((opt) => {
      const pct = total ? ((opt.votes / total) * 100).toFixed(1) : 0;
      const progressEl = opt.id === 1 ? progress1El : progress2El;
      const pctEl = opt.id === 1 ? percentage1El : percentage2El;

      progressEl.style.width = `${pct}%`;
      progressEl.textContent = `${pct}%`;
      pctEl.textContent = `${pct}% (${opt.votes} votes)`;
    });

    pieChart.data.datasets[0].data = options.map(opt => opt.votes);
    pieChart.update();
  }

  // Initial render
  updateUI();

  // Button references
  const liveResultsBtn = document.getElementById("liveResultsBtn");
  const backToPollBtn = document.getElementById("backToPollBtn");
  const shareBtn = document.getElementById("shareBtn");

  liveResultsBtn.addEventListener("click", () => {
    options.forEach(opt => {
      opt.votes += Math.floor(Math.random() * 5);
    });
    updateUI();
  });

  backToPollBtn.addEventListener("click", () => {
    window.location.href = "index.html"; // Change if your poll page is different
  });

  shareBtn.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(window.location.href);
      alert("Share link copied to clipboard!");
    } catch (err) {
      alert("Failed to copy link.");
    }
  });
});
