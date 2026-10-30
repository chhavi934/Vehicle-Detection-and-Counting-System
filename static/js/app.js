// app.js - Main JavaScript for the Vehicle Detection and Counting System

// Ensure the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Vehicle Detection System initialized');
    
    // Initialize any tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Handle alerts auto-close
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000); // Close after 5 seconds
    });
});

// Helper function to format numbers with commas
function formatNumber(num) {
    return num.toString().replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1,');
}

// Helper function to create a visualization of vehicle distribution
function createDistributionChart(carCount, truckCount, motorcycleCount, busCount) {
    // This function can be implemented if we want to add Chart.js for visualization
    // Would create a pie or bar chart showing the distribution of vehicle types
    console.log('Chart data:', { cars: carCount, trucks: truckCount, motorcycles: motorcycleCount, buses: busCount });
}
