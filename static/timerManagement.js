// Dictionary to manage active timers
const timers = {};
const circleTimerTotalDuration = 30; // Fixed total duration in seconds (depends on TTL in redis)


const startTimer = (elementId, ttl) => {
    /**
        * Starts a circular countdown timer based on a TTL value.
        *
        * The timer visually represents remaining time using a
        * conic-gradient animation and updates every second.
        *
        * @param {string} elementId - Identifier suffix for the timer element.
        * @param {number} ttl - Time-to-live value in seconds.
    */
    
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


const updateCircle = (elementId, ttl) => {
    /**
        * Updates the visual state of a circular timer immediately.
        *
        * Converts the remaining TTL into a percentage and updates
        * the corresponding circular progress indicator.
        *
        * @param {string} elementId - Identifier suffix for the timer element.
        * @param {number} ttl - Remaining time-to-live in seconds.
    */
    
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

    /**
        * Resets an existing timer with a new TTL value.
        *
        * Stops any running timer, updates the visual state immediately,
        * and restarts the countdown.
        *
        * @param {string} elementId - Identifier suffix for the timer element.
        * @param {number} ttl - New time-to-live value in seconds.
    */
    
    if (elementId && timers[elementId]) {
        clearInterval(timers[elementId]);
    }

    // Update circle immediately
    updateCircle(elementId, ttl);
    
    // Timer start
    startTimer(elementId, ttl);
};
