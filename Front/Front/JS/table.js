function adjustTableWrapper(){
	let table = document.getElementById('all-table'); /* Get reference to table element */
	let tableWrapper = document.querySelector('.table-wrapper'); /* Get reference to the 'table-wrapper class */
	if(table && tableWrapper){
		let tableHeight = table.offsetHeight || table.clientHeight || table.scrollHeight; /* Retrieve the table height through several means */
		tableWrapper.style.height = tableHeight + 'px';
	}
}

adjustTableWrapper();
