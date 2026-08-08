document.addEventListener('DOMContentLoaded', () => {
    
    // Initialize tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))

    // Form Validation (Bootstrap)
    const forms = document.querySelectorAll('.needs-validation')
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault()
                event.stopPropagation()
            }
            form.classList.add('was-validated')
        }, false)
    })

    // Loading Overlay Logic
    const predictBtns = document.querySelectorAll('.btn-predict');
    const loadingOverlay = document.getElementById('loadingOverlay');
    
    predictBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            const form = this.closest('form');
            if (form && form.checkValidity()) {
                // Show loader
                loadingOverlay.classList.remove('d-none');
                setTimeout(() => {
                    loadingOverlay.classList.add('show');
                }, 10); // Small delay to allow display block to apply before opacity transition
            }
        });
    });

    // Dark Mode Toggle
    const darkModeToggle = document.getElementById('darkModeToggle');
    const icon = darkModeToggle ? darkModeToggle.querySelector('i') : null;
    
    // Check saved preference or system preference
    const prefersDarkScheme = window.matchMedia("(prefers-color-scheme: dark)");
    const currentTheme = localStorage.getItem("theme");
    
    if (currentTheme == "dark") {
        document.body.setAttribute("data-theme", "dark");
        if(icon) {
            icon.classList.remove('fa-moon');
            icon.classList.add('fa-sun');
        }
    } else if (currentTheme == "light") {
        document.body.setAttribute("data-theme", "light");
    } else if (prefersDarkScheme.matches) {
        document.body.setAttribute("data-theme", "dark");
        if(icon) {
            icon.classList.remove('fa-moon');
            icon.classList.add('fa-sun');
        }
    }

    if (darkModeToggle) {
        darkModeToggle.addEventListener("click", function() {
            let theme = document.body.getAttribute("data-theme");
            if (theme == "dark") {
                document.body.setAttribute("data-theme", "light");
                localStorage.setItem("theme", "light");
                icon.classList.remove('fa-sun');
                icon.classList.add('fa-moon');
            } else {
                document.body.setAttribute("data-theme", "dark");
                localStorage.setItem("theme", "dark");
                icon.classList.remove('fa-moon');
                icon.classList.add('fa-sun');
            }
            
            // If Chart.js is present, update chart text colors if needed
            // A page reload is simpler for redrawing charts with new theme colors, 
            // but for now we just change CSS vars which handles most of it.
        });
    }

    // Number Counter Animation for Result Page
    const counter = document.querySelector('.counter');
    if (counter) {
        const target = +counter.getAttribute('data-target');
        const duration = 1500; // ms
        const increment = target / (duration / 16); // 60fps
        let current = 0;

        const updateCounter = () => {
            current += increment;
            if (current < target) {
                counter.innerText = current.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
                requestAnimationFrame(updateCounter);
            } else {
                counter.innerText = target.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
            }
        };
        updateCounter();
    }
});
