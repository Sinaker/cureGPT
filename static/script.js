const dropdowns = document.querySelectorAll(".dropdown");

dropdowns.forEach((dropdown) => {
	const select = dropdown.querySelector(".select");
	const caret = dropdown.querySelector(".caret");
	const menu = dropdown.querySelector(".menu");
	const options = dropdown.querySelectorAll(".menu li");
	const selected = dropdown.querySelector(".selected");

	dropdown.addEventListener("click", (e) => {
		select.classList.toggle("select-clicked");
		caret.classList.toggle("caret-rotate");
		menu.classList.toggle("menu-open");
	});

	options.forEach((option) => {
		option.addEventListener("click", () => {
			selected.innerText = option.innerText;
			e.stopPropagation();
			select.classList.remove("select-clicked");
			caret.classList.remove("caret-rotate");
			menu.classList.remove("menu-open");
			options.forEach((option) => {
				option.classList.remove("active");
			});
			option.classList.add("active");
		});
	});
});
const container = document.querySelector(".container");
window.addEventListener("load", () => {});

const submit = document.querySelector(".submit");
const help = document.querySelector(".container-main");
const inputPrompt = document.getElementById("prompt");
const loadingBar = document.querySelector(".loading-bar");

function startLoading() {
	loadingBar.classList.add("loading");
}

function stopLoading() {
	loadingBar.classList.remove("loading");
}

inputPrompt.addEventListener("keydown", (event) => {
	if (event.key === "Enter") {
		Enter();
	}
});

submit.addEventListener("click", Enter);
function Enter() {
	help.parentNode.removeChild(help);
}
const sidebar = document.getElementById("sidebar");
const sidebarToggle = document.getElementById("sidebarToggle");
const mainContent = document.getElementById("mainContent");
const navbar = document.querySelector(".container");
// Handle sidebar toggle
sidebarToggle.addEventListener("click", () => {
	sidebar.classList.toggle("active");
	mainContent.classList.toggle("shifted");
	navbar.classList.toggle("shifted"); // Shift the navbar as well
});

// Add this at the end of your existing JavaScript file

// Get loader element
const loaderOverlay = document.getElementById('loaderOverlay');

// Better loading function
function startLoading() {
    if (loaderOverlay) {
        loaderOverlay.classList.add('active');
    }
    if (loadingBar) {
        loadingBar.classList.add('loading');
    }
}

// Better stop loading function
function stopLoading() {
    if (loaderOverlay) {
        loaderOverlay.classList.remove('active');
    }
    if (loadingBar) {
        loadingBar.classList.remove('loading');
    }
}

// Error handling function
function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message || "An error occurred. Please try again.";
    
    // Add to prediction area
    const predictionArea = document.querySelector('.prediction');
    if (predictionArea) {
        predictionArea.appendChild(errorDiv);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            errorDiv.style.opacity = '0';
            setTimeout(() => errorDiv.remove(), 300);
        }, 5000);
    }
}

// Improve the existing AJAX request with proper error handling
$(document).ready(function() {
    const promptForm = document.getElementById('promptForm');
    
    if (promptForm) {
        promptForm.addEventListener('submit', function(event) {
            event.preventDefault();
            
            let userInput = $("#prompt").val();
            if (!userInput.trim()) return;
            
            // Start loading animation
            startLoading();
            
            $.ajax({
                url: "/predict",
                type: "POST",
                data: $(this).serialize(),
                success: function(response) {
                    console.log(response);
                    
                    // Stop loading
                    stopLoading();
                    
                    let newEntry = document.createElement('div');
                    newEntry.classList.add('entry');
                    
                    let inputDiv = document.createElement('div');
                    inputDiv.classList.add('input');
                    inputDiv.innerText = `You: ${userInput}`;
                    
                    let outputDiv = document.createElement('div');
                    outputDiv.classList.add('output');
                    outputDiv.innerText = `Response: ${response}`;
                    
                    newEntry.appendChild(inputDiv);
                    newEntry.appendChild(outputDiv);
                    
                    document.querySelector('.prediction').appendChild(newEntry);
                    addToHistory(userInput);
                    
                    $("#promptForm")[0].reset();
                    $("input").blur();
                    
                    updateSidebar();
                },
                error: function(xhr, status, error) {
                    // Stop loading
                    stopLoading();
                    
                    // Show error message
                    console.error("Error:", error);
                    showError("Failed to analyze symptoms. Please try again.");
                },
                timeout: 30000 // 30 second timeout
            });
        });
    }
    
    // Prevent original form from submitting if exists
    if (submit) {
        submit.removeEventListener('click', Enter);
        submit.addEventListener('click', function(e) {
            e.preventDefault();
            $('#promptForm').submit();
        });
    }
    
    // Handle Enter key properly
    if (inputPrompt) {
        inputPrompt.removeEventListener('keydown', function(event) {
            if (event.key === "Enter") {
                Enter();
            }
        });
        
        inputPrompt.addEventListener('keydown', function(event) {
            if (event.key === "Enter") {
                event.preventDefault();
                $('#promptForm').submit();
            }
        });
    }
    
    // Global error handler
    window.addEventListener('error', function(event) {
        console.error('JS Error:', event.error);
        showError("Something went wrong. Please refresh the page.");
    });
});

// Safe addToHistory function with error handling
function addToHistory(userInput) {
    try {
        const historyList = document.getElementById('historyList');
        if (historyList) {
            const newListItem = document.createElement('li');
            newListItem.innerText = userInput;
            historyList.appendChild(newListItem);
        }
    } catch (error) {
        console.error("Error adding to history:", error);
    }
}

// Safe updateSidebar function with error handling
function updateSidebar() {
    try {
        $.ajax({
            url: '/get_user_data',
            type: 'GET',
            success: function(data) {
                if (Array.isArray(data)) {
                    populateSidebar(data.reverse());
                } else {
                    console.error("Invalid data format received:", data);
                }
            },
            error: function(xhr, status, error) {
                console.error('Failed to fetch user data:', error);
            }
        });
    } catch (error) {
        console.error("Error updating sidebar:", error);
    }
}
