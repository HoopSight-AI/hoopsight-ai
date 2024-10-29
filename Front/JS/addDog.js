document.getElementById('add-pet-button').addEventListener('click', function(){
	const petsContainer = document.getElementById('pet-fields-container');

	if(petsContainer){
		
		/********************* CHILD ELEMENTS OF pet-field-container **********************/
		const fieldsContainer = document.createElement('div');
		fieldContainer = fieldsContainer.className = 'fields-container';

		//petFieldsContainer.innerHTML = `<div id='pet-fields-container' class='pet-field-container'>`;
		//Lesson learned: .innerHTML will create a child element of the newly created field. Use DOM object attributes to assign characteristics to an HTML element using JavaScript	

			/********************* CHILD ELEMENTS OF field-container **********************/
				const textFieldWrapper = document.createElement('div');
				textFieldWrapper.className = 'individual-text-field-wrapper';
	
					/********************* CHILD ELEMENTS OF textFieldWrapper **********************/
					const textInput = document.createElement('input');
					textInput.className = 'text-field';
					textInput.type = 'text';
					textInput.name = 'pet-name[]';
					textInput.placeholder = 'Pet name';
					textInput.required = true;				
	
					const placeHolder = document.createElement('div');
					placeHolder.className = 'input-placeholder';
        				placeHolder.textContent = 'New Pet name';
		
			/********************* CHILD ELEMENTS OF field-container **********************/
				const imageFieldWrapper = document.createElement('div');
				imageFieldWrapper.className = 'individual-text-field-wrapper';

					/********************* CHILD ELEMENTS OF textFieldWrapper **********************/
					const imageInput = document.createElement('input');
					imageInput.className = 'text-field';
					imageInput.type = 'file';
					imageInput.name = 'pet-image[]';
					imageInput.placeholder = 'Pet image';
					imageInput.required = true;

		//Build remove button
		const removeButton = document.createElement('button');
		removeButton.type = 'button';
		removeButton.textContent = 'Remove pet';
		removeButton.className = 'field-button';
		removeButton.addEventListener('click', function() {
		    petsContainer.removeChild(fieldsContainer);
		});
	
	//Contstruct the new field
	imageFieldWrapper.appendChild(imageInput);

	textFieldWrapper.appendChild(textInput);
	textFieldWrapper.appendChild(placeHolder);

	fieldsContainer.appendChild(textFieldWrapper);
	fieldsContainer.appendChild(imageFieldWrapper);
	fieldsContainer.appendChild(removeButton);

	petsContainer.appendChild(fieldsContainer);	
	

	} else {
		console.log('Container not found. Operation failed');
	}	
});
