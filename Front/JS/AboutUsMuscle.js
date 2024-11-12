document.addEventListener("scroll", () => {
	const scrollPosition = window.scrollY;
	const background = document.querySelector(".parallax-background");

	// Adjust parallax speed by modifying the multiplier
	background.style.transform = `translateY(${scrollPosition * 0.5}px)`;
});
