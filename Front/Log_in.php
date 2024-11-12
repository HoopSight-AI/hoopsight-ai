<?php

//declare(strict_types=1);

class PetReg
{
	private $cellId;
	private string $html = '';

	public function __construct($cellId = null)
	{
		$this->cellId = $cellId;
	}

	/**
	 * Builds the HTML for assigning kits to pets and stores it in the $html property.
	 *
	 * @param mixed $kitsWithoutPet The kit(s) without assigned pets.
	 * @param mixed $pets           The pet(s) associated with the account.
	 */
	public function buildKitAssignmentForm($kitsWithoutPet, $pets): void
	{
		if (empty($kitsWithoutPet)) {
			return;
		}

		$index = 1; // Index is used to assign a unique id to a cell

		$kitsWithoutPet = is_array($kitsWithoutPet) ? $kitsWithoutPet : [$kitsWithoutPet];
		$pets = is_array($pets) ? $pets : [$pets];

		$kitAssignmentForms = [];
		$petRegistrationForms = [];

		// Generate relevant forms per available kit
		foreach ($kitsWithoutPet as $kit) {
			$kitAssignmentForms[] = $this->generateKitAssignmentForm($kit, $pets, $index);
			$petRegistrationForms[] = $this->generatePetRegistrationForm($kit, $index);
			$index++;
		}

		// Build the HTML
		$this->html .= "<div class='all-unassigned-kit-cells'>";
		foreach ($kitAssignmentForms as $form) {
			$this->html .= $form;
		}
		$this->html .= "</div>";

		foreach ($petRegistrationForms as $form) {
			$this->html .= $form;
		}
	}

	/**
	 * Generates the HTML form for assigning a kit to an existing pet.
	 *
	 * @param object $kit   The kit object containing the necessary data.
	 * @param array  $pets  The array of pet objects associated with the account.
	 * @param int    $index The index for generating unique IDs.
	 *
	 * @return string The HTML output of the form.
	 */
	private function generateKitAssignmentForm($kit, array $pets, int $index): string
	{
		$kitId  = htmlspecialchars($kit->getId(), ENT_QUOTES, 'UTF-8');
		$kitTest = htmlspecialchars($kit->getTest(), ENT_QUOTES, 'UTF-8');
		$kitNum = htmlspecialchars($kit->getKitn(), ENT_QUOTES, 'UTF-8');

		// Generate options for the select dropdown
		$selectOptions = "<option value='' disabled selected>Select a pet</option>";
		foreach ($pets as $pet) {
			$petId = htmlspecialchars($pet->getId(), ENT_QUOTES, 'UTF-8');
			$petName = htmlspecialchars($pet->getPetname(), ENT_QUOTES, 'UTF-8');
			$selectOptions .= "<option value='$petId'>$petName</option>";
		}

		// Generate the form HTML
		$form = <<<HTML
		<div class='unassigned-kit-cell'>
			<div class='red-circle'></div>
			<div class="kit-info">
			<h2 class='first-letter-uppercase'>{$kitTest} test detected!</h2>
			<span>ID: #{$kitNum}</span>
			</div>
			<form id='kit-assign-{$index}' class='kit-assignment-form' action='formCatch.php' method='post'>
			<input type="hidden" name="existing-pet" value="YERRRRRRRRRRRR" />
			<input type="hidden" name="kit-number-meta" value="{$kitNum}" />
			<input type="hidden" name="kit-ID-meta" value="{$kitId}" />
			<div class='existing-pet-container'>
			<label for='existing-pet-name-{$index}'>Assign this test to an existing pet:</label>
			<select id='existing-pet-name-{$index}' class='drop-down' name='existing-pet-id' required>
		{$selectOptions}
		</select>
		</div>
		<input class='add-pet-button' type='submit' value='Assign Kit'>
		</form>
		<div class='hr-with-text'>
		<span>OR</span>
		</div>
		<button class="add-pet-button" id="call-pet-form-{$index}">Create New Pet</button>
		</div>
HTML;
		return $form;
	}

	/**
	 * Generates the pet registration form HTML for a specific kit.
	 *
	 * @param object $kit   The kit object containing the necessary data.
	 * @param int    $index The index for generating unique IDs.
	 *
	 * @return string The HTML output of the form.
	 */
	private function generatePetRegistrationForm($kit, int $index): string
	{
		$kitTest = htmlspecialchars($kit->getTest(), ENT_QUOTES, 'UTF-8');
		$kitNum  = htmlspecialchars($kit->getKitn(), ENT_QUOTES, 'UTF-8');
		$kitId   = htmlspecialchars($kit->getId(), ENT_QUOTES, 'UTF-8');
		$miniKitId = substr($kitNum, -4);

		// Generate years, months, weight, and height options
		$yearsOptions = $this->generateOptions(0, 100, 'years');
		$monthsOptions = $this->generateOptions(0, 11, 'months');
		$weightOptions = $this->generateOptions(1, 999, 'lb');
		$heightFtOptions = $this->generateOptions(1, 8, 'ft');
		$heightInOptions = $this->generateOptions(0, 11, 'in');

		// Generate the form HTML
		$form = <<<HTML
<div id='pet-reg-background-{$index}' class='pet-reg-background'>
   <div id='pet-reg-container-{$index}' class='pet-reg-container'>
      <form id='pet-registration-{$index}' class='kit-assignment-form' method='post' action='formCatch.php' enctype='multipart/form-data'>
         <input type="hidden" name="kit-number-meta" value="{$kitNum}" />
         <input type="hidden" name="kit-ID-meta" value="{$kitId}" />
         <span class='pet-reg-header'>Pet Registration Form</span>
         <div class="image-upload-container">
            <input class='form-pet-image' type="file" id="pet-image-{$index}" name="pet-image" accept="image/*" hidden />
            <label id="pet-image-pencil-{$index}" class="pencil-icon" for="pet-image-{$index}">&#9998;</label>
            <label id="pet-image-background-{$index}" class="image-upload-label" for="pet-image-{$index}" style="background-image: url('images/default-dog.png');"></label>
         </div>
         <div class='individual-text-field-wrapper'>
            <input class='text-field' id="pet-name-{$index}" type='text' name='pet-name' placeholder='Pet name' required />
            <div class='input-placeholder'>Pet name</div>
         </div>
         <h3>Optional Data</h3>
         <select id='measurement-type-{$index}' name='measurement-type' class='drop-down'>
            <option value='' disabled selected>Unit preference</option>
            <option value='imperial'>Imperial</option>
            <option value='metric'>Metric</option>
         </select>
         <span>Pet Age</span>
         <div class='measurement-drop-down-container'>
            <div class='dropdowns-container'>
               <select class='drop-down' name='age-years'>
                  <option value="" disabled selected>Years</option>
                  {$yearsOptions}
               </select>
               <select class='drop-down' name='age-months'>
                  <option value="" disabled selected>Months</option>
                  {$monthsOptions}
               </select>
            </div>
         </div>
         <span>Pet Weight</span>
         <div id='weight-dropdowns-container-{$index}' class='height-dropdowns-container'>
            <select class='drop-down' name='pet-weight'>
               <option value="" disabled selected>Weight (lb)</option>
               {$weightOptions}
            </select>
         </div>
         <div class='measurement-drop-down-container'>
            <span>Pet Height</span>
            <div id='height-dropdowns-container-{$index}' class='height-dropdowns-container'>
               <select class='drop-down' name='height-1'>
                  <option value="" disabled selected>Height (ft)</option>
                  {$heightFtOptions}
               </select>
               <select class='drop-down' name='height-2'>
                  <option value="" disabled selected>Height (in)</option>
                  {$heightInOptions}
               </select>
            </div>
         </div>
         <input type="submit" class="add-pet-button">
         <span class='pet-reg-fine'>Will automatically assign new pet to {$kitTest} test #...{$miniKitId}</span>
      </form>
   </div>
</div>
HTML;
		return $form;
	}

	/**
	 * Generates HTML options for select inputs.
	 *
	 * @param int    $start The starting number.
	 * @param int    $end   The ending number.
	 * @param string $unit  The unit to display.
	 *
	 * @return string The generated HTML options.
	 */
	private function generateOptions(int $start, int $end, string $unit): string
	{
		$options = '';
		for ($i = $start; $i <= $end; $i++) {
			$options .= "<option value='{$i} {$unit}'>{$i} {$unit}</option>";
		}
		return $options;
	}

	/**
	 * Outputs the generated HTML.
	 */
	public function displayHtml(): void
	{
		echo $this->html;
	}

	/**
	 * Retrieves the generated HTML.
	 *
	 * @return string The generated HTML.
	 */
	public function getHtml(): string
	{
		return $this->html;
	}
}
