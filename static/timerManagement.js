// Dictionary to manage active timers
const timers = {};
const circleTimerTotalDuration = 30; // Fixed total duration in seconds (depends on TTL in redis)

// Fonction pour démarrer un timer
const startTimer = (elementId, ttl) => {
    const circle = document.getElementById(`circle_${elementId}`);
    const totalDuration = circleTimerTotalDuration;
    
    const interval = setInterval(() => {
        // Calculates the exact percentage based on the current TTL
        const percentage = 1 - (ttl / totalDuration);
        
        // Converts percentage to degrees (360 degrees is a full circle)
        const degrees = percentage * 360;
        if (circle) {
            // Update the circle with a conical gradient
            circle.style.background = `conic-gradient(#f9f9f9 ${degrees}deg, #6082b6 ${degrees}deg)`;
        }
        
        // Reduce TTL at each iteration
        ttl--;
        
        // Stop the timer when the TTL reaches 0
        if (ttl <= 0) {
            clearInterval(interval);
            delete timers[elementId];
        }
    }, 1000);
    
    timers[elementId] = interval;
}

// Update circle immediately function
const updateCircle = (elementId, ttl) => {
    const circle = document.getElementById(`circle_${elementId}`);
    const totalDuration = circleTimerTotalDuration; 
    const percentage = 1 - (ttl / totalDuration);
    const degrees = percentage * 360;
    
    if (circle) {
        circle.style.background = `conic-gradient(#f9f9f9 ${degrees}deg, #6082b6 ${degrees}deg)`;
    }
};

// Reset a timer with a new TTL function
export const resetTimer = (elementId, ttl) => {
    if (elementId && timers[elementId]) {
        clearInterval(timers[elementId]);
    }
    // Update circle immediately
    updateCircle(elementId, ttl);
    
    // Timer start
    startTimer(elementId, ttl);
};
