<?php
session_start();
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <?php include 'Front/Content/HTMLhead.php'; ?>
    <link rel="stylesheet" href="Front/CSS/style.css">
    <link rel="stylesheet" href="Front/CSS/legacy-style.css">
    <link rel="icon" type="image/x-icon" href="Front/Assets/ball-icon.ico">
</head>
<body>
    <!-- Header Section -->
    <header>
        <?php include 'Front/Content/HTMLheader.php'; ?>
    </header>

    <!-- Main Content -->
    <main class="container">
        <div class="content-wrapper">
            <!-- Image Upload Section -->
            <section class="upload-section">
                <h2>Upload Basketball Image</h2>
                <form id="imageUploadForm" enctype="multipart/form-data">
                    <div class="upload-container">
                        <input type="file" id="imageInput" accept="image/*" required>
                        <button type="submit" class="upload-btn">Analyze Image</button>
                    </div>
                </form>
            </section>

            <!-- Results Section -->
            <section class="results-section">
                <div id="loadingSpinner" class="spinner" style="display: none;">
                    <div class="spinner-border" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                </div>
                <div id="resultContainer" class="result-container"></div>
            </section>

            <!-- Muscle Analysis Table -->
            <section class="muscle-analysis">
                <div id="tableContainer"></div>
            </section>
        </div>
    </main>

    <!-- Footer Section -->
    <footer>
        <?php include 'Front/Content/HTMLfooter.php'; ?>
    </footer>

    <!-- JavaScript Files -->
    <script src="Front/JS/muscle.js"></script>
    <script src="Front/JS/dominoMuscle.js"></script>
    <script src="Front/JS/table.js"></script>
    <script src="Front/JS/addDog.js"></script>
    <script src="Front/JS/addDogV2.js"></script>

    <script>
        document.getElementById('imageUploadForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData();
            const imageFile = document.getElementById('imageInput').files[0];
            
            if (!imageFile) {
                alert('Please select an image first');
                return;
            }

            formData.append('image', imageFile);
            
            // Show loading spinner
            document.getElementById('loadingSpinner').style.display = 'block';
            document.getElementById('resultContainer').innerHTML = '';

            try {
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();
                
                if (data.success) {
                    // Handle successful response
                    document.getElementById('resultContainer').innerHTML = `
                        <div class="analysis-result">
                            <h3>Analysis Results</h3>
                            <p>${data.message}</p>
                        </div>
                    `;
                } else {
                    // Handle error
                    document.getElementById('resultContainer').innerHTML = `
                        <div class="error-message">
                            <p>Error: ${data.message}</p>
                        </div>
                    `;
                }
            } catch (error) {
                console.error('Error:', error);
                document.getElementById('resultContainer').innerHTML = `
                    <div class="error-message">
                        <p>An error occurred during analysis. Please try again.</p>
                    </div>
                `;
            } finally {
                // Hide loading spinner
                document.getElementById('loadingSpinner').style.display = 'none';
            }
        });
    </script>
</body>
</html>
