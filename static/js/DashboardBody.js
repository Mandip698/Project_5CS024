const polls = [
    {
        title: 'PM',
        date: 'Mar 16, 2025',
        time: '8:48 AM',
        status: 'Closed'
    },
    {
        title: 'Election',
        date: 'Apr 10, 2025',
        time: '10:00 AM',
        status: 'Open'
    }
];

function loadPolls() {
    const pollList = document.getElementById('pollList');
    pollList.innerHTML = '';

    polls.forEach(poll => {
        const pollCard = document.createElement('div');
        pollCard.className = 'poll-card d-flex justify-content-between align-items-center';

        pollCard.innerHTML = `
            <div>
                <h5>${poll.title}</h5>
                <small>${poll.date} - ${poll.time}</small>
            </div>
            <span class="badge ${poll.status === 'Closed' ? 'status-closed' : 'badge-success'}">${poll.status}</span>
        `;

        pollList.appendChild(pollCard);
    });
}

document.getElementById('sortSelect').addEventListener('change', (e) => {
    if (e.target.value === 'deadline') {
        polls.sort((a, b) => new Date(a.date) - new Date(b.date));
    } else {
        polls.sort((a, b) => a.title.localeCompare(b.title));
    }
    loadPolls();
});

loadPolls();