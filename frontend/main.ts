document.addEventListener('DOMContentLoaded', () => {
    const imageUpload = document.getElementById('imageUpload') as HTMLInputElement;
    const imagePreview = document.getElementById('imagePreview') as HTMLImageElement;
    const imagePreviewContainer = document.getElementById('imagePreviewContainer') as HTMLDivElement;
    const analyzeButton = document.getElementById('analyzeButton') as HTMLButtonElement;
    const analysisText = document.getElementById('analysisText') as HTMLParagraphElement;
    const resultsContainer = document.getElementById('results') as HTMLDivElement;
    const loadingIndicator = document.getElementById('loadingIndicator') as HTMLDivElement;
    const errorMessagesDiv = document.getElementById('errorMessages') as HTMLDivElement;
    const errorTextP = document.getElementById('errorText') as HTMLParagraphElement;

    let currentFile: File | null = null;

    if (!imageUpload || !imagePreview || !analyzeButton || !analysisText || !resultsContainer || !imagePreviewContainer || !loadingIndicator || !errorMessagesDiv || !errorTextP) {
        console.error('One or more essential HTML elements are missing.');
        if (errorMessagesDiv && errorTextP) {
            errorTextP.textContent = 'Initialization error: Page elements missing. Please contact support.';
            errorMessagesDiv.style.display = 'block';
        }
        return;
    }

    analyzeButton.disabled = true; // Disable button initially

    imageUpload.addEventListener('change', (event) => {
        const files = (event.target as HTMLInputElement).files;
        console.log("Event target", event.target);
        console.log("Files", files);
        // If files is indeed a FileList (a list of files), the .length property tells you how many files are in that list.
        console.log("Files length", files === null || files === void 0 ? void 0 : files.length);
        console.log("Current file", currentFile);
        console.log("Image preview", imagePreview);
        console.log("Image preview container", imagePreviewContainer);
        console.log("Analyze button", analyzeButton);
        console.log("Analysis text", analysisText);
        if (files && files.length > 0) {
            currentFile = files[0];
            // console.log("Files_v2", files);
            // console.log("Files0", files[0]);
            console.log("Current file_v2", currentFile);
            // The FileReader object is created first, and then one of its methods is called to initiate the reading process for a specific file.
            // This object can read files in different formats (text, binary, data URL, etc.)

            const reader = new FileReader();

            // reader.onload = (e) => { ... }; (Setting up the "What To Do Next")
            // This line prepares the reader object.
            // You're telling the reader: "Hey, I'm going to ask you to read a file soon. 
            // When you are successfully finished reading it, please execute this function I'm giving you."
            reader.onload = (e) => {
                if (e.target && e.target.result) {
                    console.log("e.target.result", e.target.result);
                    console.log("e.target", e.target);

                    // The .src property of an <img> element is where you specify the URL of the image to be displayed.
                    imagePreview.src = e.target.result as string;
                    console.log("imagePreview.src", imagePreview.src);
                    imagePreview.style.display = 'block';
                    imagePreviewContainer.style.display = 'flex'; // Show container
                    analyzeButton.disabled = false; // Enable button when image is selected
                    analysisText.textContent = 'Image loaded. Click \"Analyze Image\".';
                    resultsContainer.style.display = 'none'; // Hide previous results
                    errorMessagesDiv.style.display = 'none'; // Hide previous errors
                }
            };
            // This starts the asynchronous reading process
            // The readAsDataURL() method converts the file into a base64-encoded data URL
            // Here's the chronological flow:
            // User selects file → change event fires
            // FileReader created → new FileReader()
            // Event handler attached → reader.onload = (e) => { ... }
            // Reading initiated → reader.readAsDataURL(currentFile)
            // Browser reads file → (asynchronous process)
            // Reading completes → onload event fires
            // Event handler executes → Updates UI with image preview
            reader.readAsDataURL(currentFile);

        } else {
            currentFile = null;
            imagePreview.style.display = 'none';
            imagePreviewContainer.style.display = 'none';
            analyzeButton.disabled = true;
            analysisText.textContent = 'Waiting for analysis...';
        }
    });

    // addEventListener - Attaches an event listener to the analyze button
    // 'click' - Listens specifically for click events on the button
    // async - Makes the function asynchronous, allowing use of await for API calls later
    analyzeButton.addEventListener('click', async () => {
        if (!currentFile) {
            errorTextP.textContent = 'Please select an image file first.';
            errorMessagesDiv.style.display = 'block';
            return;
        }

        console.log('==== ANALYZE BUTTON CLICKED ====');
        console.log('Current file:', currentFile);
        
        console.log('Creating FormData...');
        const formData = new FormData();
        formData.append('image', currentFile);

        console.log("FormData object:", formData); // This will likely show an empty object or FormData specific representation

        console.log("%c FormData entries: ", "color: green; font-weight: bold;");
        for (const pair of formData.entries()) {
            console.log(`  ${pair[0]}: ${pair[1]}`);
        }
        // To get a specific value:
        // console.log("\nValue for 'image' key:", formData.get('image'));
        // Show loading indicator and disable button
        loadingIndicator.style.display = 'block';
        analyzeButton.disabled = true;
        resultsContainer.style.display = 'none';
        errorMessagesDiv.style.display = 'none';
        analysisText.textContent = ''; // Clear previous analysis

        try {
            // Get the API base URL (handles both Electron and browser environments)
            const apiBaseUrl = (window as any).electronUtils?.getApiBaseUrl?.() || 'http://localhost:5001';
            const response = await fetch(`${apiBaseUrl}/upload`, {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                let errorMsg = `Error: ${response.status} ${response.statusText}`;
                try {
                    const errorData = await response.json();
                    errorMsg = errorData.error || errorMsg;
                } catch (e) {
                    // If parsing error JSON fails, use the status text
                }
                throw new Error(errorMsg);
            }

            const result = await response.json();
            
            if (result.analysis) {
                analysisText.textContent = result.analysis;
            } else if (result.error) {
                analysisText.textContent = `Analysis Error: ${result.error}`;
            } else {
                analysisText.textContent = 'Received an unexpected response from the server.';
            }
            resultsContainer.style.display = 'block';

        } catch (error: any) {
            console.error('Error uploading or analyzing image:', error);
            errorTextP.textContent = `An error occurred: ${error.message || 'Unknown error'}`;
            errorMessagesDiv.style.display = 'block';
            analysisText.textContent = 'Failed to get analysis.'; // Update main analysis text too
            resultsContainer.style.display = 'block'; // Show results container to display this message
        } finally {
            // Hide loading indicator and re-enable button
            loadingIndicator.style.display = 'none';
            // Only re-enable if there's a file selected, otherwise it should remain disabled
            if (currentFile) {
                 analyzeButton.disabled = false;
            }
        }
    });
});
