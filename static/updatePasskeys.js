import { resetTimer } from "./timerManagement.js";


export const updatePasskeys = (socket, userId, clientPasskeyElement, advisorPasskeyElement) => {
    /** 
        * Manages real-time passkey updates via Socket.IO.
        *
        * Listens for passkey update events, updates the UI securely,
        * resets timers, handles internationalization, and ensures
        * proper cleanup of listeners and intervals.
        *
        * @param {Object} socket - Active Socket.IO connection.
        * @param {string} userId - Client identifier.
        * @param {HTMLElement} clientPasskeyElement - DOM element displaying client passkey.
        * @param {HTMLElement} advisorPasskeyElement - DOM element displaying advisor passkey.
        *
        * @returns {Function} Cleanup function to remove listeners and intervals.
    */

    // Variables to manage intervals and listeners
    let passkeyUpdateInterval = null;
    let isUpdating = false;
    
    // Secure update feature with i18n support
    const updatePasskeyDisplay = (data) => {
        /**
            * Updates passkey values and UI state in real time.
            *
            * Validates incoming data, updates client and advisor passkeys,
            * applies visual states (expired / updating), refreshes localized
            * instructions, and resets the associated countdown timer.
            *
            * Concurrent updates are prevented using a locking mechanism.
            *
            * @param {Object} data - Payload received from the Socket.IO event.
            * @param {Object} data.client - Client passkey and TTL information.
            * @param {Object} data.advisor_client - Advisor passkey and TTL information.
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
            if (clientPasskeyElement) {
                clientPasskeyElement.textContent = data.client.user_passkey || i18next.t('updating');
                clientPasskeyElement.classList.toggle('updating-text', data.client.user_ttl < 1);
                
                const clientPasskeyBox = clientPasskeyElement.closest('.passkey-box');
                if (clientPasskeyBox) {
                    const instruction = clientPasskeyBox.querySelector('.instruction[data-i18n]');
                    if (instruction) {
                        instruction.textContent = i18next.t(instruction.getAttribute('data-i18n'));
                    }
                }
            }
            
            if (advisorPasskeyElement) {
                advisorPasskeyElement.textContent = data.advisor_client.advisor_passkey || i18next.t('updating');
                advisorPasskeyElement.classList.toggle('updating-text', data.advisor_client.advisor_ttl < 1);

                const advisorPasskeyBox = advisorPasskeyElement.closest('.passkey-box');
                if (advisorPasskeyBox) {
                    const instruction = advisorPasskeyBox.querySelector('.instruction[data-i18n]');
                    if (instruction) {
                        instruction.textContent = i18next.t(instruction.getAttribute('data-i18n'));
                    }
                }
            }
            
            // Timer reset
            resetTimer('client', data.client.user_ttl);
            
            isUpdating = false;
        } catch (error) {
            console.error('Error updating passkeys:', error);
            isUpdating = false;
        }
    };
    

    const cleanupSocketListeners = () => {
        /**
            * Cleans up Socket.IO listeners and running intervals.
            *
            * Removes passkey update listeners and clears the periodic
            * update interval to prevent memory leaks or duplicated events.
        */
        
        socket.off('update_passkeys_pairs', updatePasskeyDisplay);
        if (passkeyUpdateInterval) {
            clearInterval(passkeyUpdateInterval);
            passkeyUpdateInterval = null;
        }
    };
    
    // Initial cleaning
    cleanupSocketListeners();
    
    // New secure configuration
    socket.on('update_passkeys_pairs', updatePasskeyDisplay);
    
    // First synchronization
    socket.emit('request_update', { user_id: userId });
    
    // Secure update interval
    passkeyUpdateInterval = setInterval(() => {
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
