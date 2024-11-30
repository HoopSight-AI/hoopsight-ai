const stuff = [
	{ shortName: "Golden State", fullName: "Golden State Warriors" },
	{ shortName: "LA Clippers", fullName: "Los Angeles Clippers" },
	{ shortName: "Milwaukee", fullName: "Milwaukee Bucks" },
	{ shortName: "Detroit", fullName: "Detroit Pistons" },
	{ shortName: "Charlotte", fullName: "Charlotte Hornets" },
	{ shortName: "Portland", fullName: "Portland Trail Blazers" },
	{ shortName: "Indiana", fullName: "Indiana Pacers" },
	{ shortName: "LA Lakers", fullName: "Los Angeles Lakers" },
	{ shortName: "Brooklyn", fullName: "Brooklyn Nets" },
	{ shortName: "Cleveland", fullName: "Cleveland Cavaliers" },
	{ shortName: "Washington", fullName: "Washington Wizards" },
	{ shortName: "Utah", fullName: "Utah Jazz" },
	{ shortName: "Atlanta", fullName: "Atlanta Hawks" },
	{ shortName: "Phoenix", fullName: "Phoenix Suns" },
	{ shortName: "New Orleans", fullName: "New Orleans Pelicans" },
	{ shortName: "Memphis", fullName: "Memphis Grizzlies" },
	{ shortName: "Denver", fullName: "Denver Nuggets" },
	{ shortName: "Okla City", fullName: "Oklahoma City Thunder" },
	{ shortName: "Dallas", fullName: "Dallas Mavericks" },
	{ shortName: "Boston", fullName: "Boston Celtics" },
	{ shortName: "New York", fullName: "New York Knicks" },
	{ shortName: "Sacramento", fullName: "Sacramento Kings" },
	{ shortName: "San Antonio", fullName: "San Antonio Spurs" },
	{ shortName: "Chicago", fullName: "Chicago Bulls" },
	{ shortName: "Minnesota", fullName: "Minnesota Timberwolves" },
	{ shortName: "Miami", fullName: "Miami Heat" },
	{ shortName: "Orlando", fullName: "Orlando Magic" },
	{ shortName: "Philadelphia", fullName: "Philadelphia 76ers" },
	{ shortName: "Toronto", fullName: "Toronto Raptors" },
	{ shortName: "Houston", fullName: "Houston Rockets" },
];

/**
 * PredictionApp Class
 * Manages the team dropdown, cycling of teams, and fetching predictions.
 */
class PredictionApp {
	/**
	 * Constructor initializes the app.
	 * @param {string} dropdownId - The ID of the dropdown element.
	 * @param {string} fetchButtonId - The ID of the fetch button element.
	 * @param {string} predictionTableId - The ID of the prediction table container.
	 */
	constructor(dropdownId, fetchButtonId, predictionTableId) {
		this.dropdown = document.getElementById(dropdownId);
		this.fetchButton = document.getElementById(fetchButtonId);
		this.predictionTable = document.getElementById(predictionTableId);

		// TODO: There has to be a better way for us to generate the team names.
		//Perhaps we can pull team names from somewhere else so names get
		//populated automatically.
		this.teams = stuff;

		this.cyclingInterval = null;

		this.populateDropdown();
		this.startCycling();
		this.addEventListeners();
	}

	/**
	 * Populates the dropdown with team options.
	 */
	populateDropdown() {
		this.dropdown.innerHTML = "";
		for (let team of this.teams) {
			let option = document.createElement("option");
			// Set value as shortName and display fullName
			option.value = team.shortName;
			option.textContent = team.fullName;
			this.dropdown.appendChild(option);
		}
	}

	/**
	 * Starts cycling the team names in the dropdown every 2.5 seconds.
	 */
	startCycling() {
		this.cyclingInterval = setInterval(() => {
			this.teams.push(this.teams.shift()); // Rotate team names
			this.populateDropdown();
		}, 2500);
	}

	/**
	 * Stops cycling the team names.
	 */
	stopCycling() {
		clearInterval(this.cyclingInterval);
	}

	/**
	 * Adds event listeners to the dropdown and fetch button.
	 */
	addEventListeners() {
		// Handle button click to fetch predictions
		this.fetchButton.addEventListener("click", () => this.fetchPredictions());

		// Stop cycling when dropdown is clicked
		this.dropdown.addEventListener("click", () => this.stopCycling());
	}

	/**
	 * Fetches predictions for the selected team and displays them.
	 */
	fetchPredictions() {
		const selectedTeam = this.dropdown.value;
		if (!selectedTeam) {
			alert("Please select a team!");
			return;
		}

		// Fetch predictions for the selected team
		fetch("FetchPredictions.php?team=" + encodeURIComponent(selectedTeam))
			.then((response) => response.text())
			.then((data) => {
				this.predictionTable.innerHTML = data;
			})
			.catch((err) => console.error("Error fetching predictions:", err));
	}
}

// Initialize the PredictionApp after the DOM content is loaded
document.addEventListener("DOMContentLoaded", () => {
	const app = new PredictionApp(
		"team-dropdown", // ID of the dropdown element
		"fetch-predictions", // ID of the fetch button
		"prediction-table" // ID of the prediction table container
	);
});
