function submitVote() {
    const selectedOption = document.querySelector('input[name="pollOption"]:checked');
    if (selectedOption) {
      alert(`You voted for: ${selectedOption.value}`);
    } else {
      alert("Please select an option to vote.");
    }
  }
  
  function showResults() {
    alert("Displaying poll results... (this can be replaced with real results UI)");
  }
  