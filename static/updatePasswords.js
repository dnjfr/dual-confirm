import { resetTimer } from "./timerManagement.js";

/// Update passwords in real time function
export const updatePasswords = (socket, userId, clientPwdElement, advisorPwdElement) => {
    // Variables to manage intervals and listeners
    let passwordUpdateInterval = null;
    let isUpdating = false;
    
    // Secure update feature with i18n support
    const updatePasswordDisplay = (data) => {
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
    
    // Complete cleaning before new configuration
    const cleanupSocketListeners = () => {
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
    
    // Logout manager
    const handleDisconnect = () => {
        cleanupSocketListeners();
    };
    
    socket.on('disconnect', handleDisconnect);
    
    // Return a cleanup function
    return () => {
        cleanupSocketListeners();
        socket.off('disconnect', handleDisconnect);
    };
};
