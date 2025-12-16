import { resetTimer } from "./timerManagement.js";


export const updatePasswords = (socket, userId, clientPwdElement, advisorPwdElement) => {
    /** 
        * Manages real-time password updates via Socket.IO.
        *
        * Listens for password update events, updates the UI securely,
        * resets timers, handles internationalization, and ensures
        * proper cleanup of listeners and intervals.
        *
        * @param {Object} socket - Active Socket.IO connection.
        * @param {string} userId - Client identifier.
        * @param {HTMLElement} clientPwdElement - DOM element displaying client password.
        * @param {HTMLElement} advisorPwdElement - DOM element displaying advisor password.
        *
        * @returns {Function} Cleanup function to remove listeners and intervals.
    */

    // Variables to manage intervals and listeners
    let passwordUpdateInterval = null;
    let isUpdating = false;
    
    // Secure update feature with i18n support
    const updatePasswordDisplay = (data) => {
        /**
            * Updates password values and UI state in real time.
            *
            * Validates incoming data, updates client and advisor passwords,
            * applies visual states (expired / updating), refreshes localized
            * instructions, and resets the associated countdown timer.
            *
            * Concurrent updates are prevented using a locking mechanism.
            *
            * @param {Object} data - Payload received from the Socket.IO event.
            * @param {Object} data.client - Client password and TTL information.
            * @param {Object} data.advisor_client - Advisor password and TTL information.
        */

        // Avoid simultaneous updates
        if (isUpdating) return;
        
        isUpdating = true;
        
        try {
            // Strict data validation
            if (!data || data.error || !data.client || !data.advisor_client) {
                console.error('Données invalides', data);
                isUpdating = false;
                return;
            }
            
            // Update items
            if (clientPwdElement) {
                clientPwdElement.textContent = data.client.user_pwd || i18next.t('updating');
                clientPwdElement.classList.toggle('updating-text', data.client.user_ttl < 1);
                
                const clientPwdBox = clientPwdElement.closest('.password-box');
                if (clientPwdBox) {
                    const instruction = clientPwdBox.querySelector('.instruction[data-i18n]');
                    if (instruction) {
                        instruction.textContent = i18next.t(instruction.getAttribute('data-i18n'));
                    }
                }
            }
            
            if (advisorPwdElement) {
                advisorPwdElement.textContent = data.advisor_client.advisor_pwd || i18next.t('updating');
                advisorPwdElement.classList.toggle('updating-text', data.advisor_client.advisor_ttl < 1);

                const advisorPwdBox = advisorPwdElement.closest('.password-box');
                if (advisorPwdBox) {
                    const instruction = advisorPwdBox.querySelector('.instruction[data-i18n]');
                    if (instruction) {
                        instruction.textContent = i18next.t(instruction.getAttribute('data-i18n'));
                    }
                }
            }
            
            // Timer reset
            resetTimer('client', data.client.user_ttl);
            
            isUpdating = false;
        } catch (error) {
            console.error('Error updating passwords:', error);
            isUpdating = false;
        }
    };
    

    const cleanupSocketListeners = () => {
        /**
            * Cleans up Socket.IO listeners and running intervals.
            *
            * Removes password update listeners and clears the periodic
            * update interval to prevent memory leaks or duplicated events.
        */
        
        socket.off('update_passwords', updatePasswordDisplay);
        if (passwordUpdateInterval) {
            clearInterval(passwordUpdateInterval);
            passwordUpdateInterval = null;
        }
    };
    
    // Initial cleaning
    cleanupSocketListeners();
    
    // New secure configuration
    socket.on('update_passwords', updatePasswordDisplay);
    
    // First synchronization
    socket.emit('request_update', { user_id: userId });
    
    // Secure update interval
    passwordUpdateInterval = setInterval(() => {
        if (!isUpdating) {
            socket.emit('request_update', { user_id: userId });
        }
    }, 1000);
    
    
    const handleDisconnect = () => {
        /**
            * Handles socket disconnection events.
            *
            * Ensures all listeners and intervals are properly cleaned
            * when the socket connection is terminated.
        */
        
        cleanupSocketListeners();
    };
    
    socket.on('disconnect', handleDisconnect);
    
    // Return a cleanup function
    return () => {
        cleanupSocketListeners();
        socket.off('disconnect', handleDisconnect);
    };
};
