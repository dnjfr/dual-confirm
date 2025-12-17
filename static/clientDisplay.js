// Display customer data in the advisor interface function
export const clientDisplay = (clientAuthDiv, data, localizeContent) => {

    /**
        * Renders client information and authentication data
        * inside the advisor interface.
        *
        * This function dynamically builds the DOM structure
        * for client details, passkeys, and countdown timer,
        * then applies internationalization.
        *
        * @param {HTMLElement} clientAuthDiv - Container element for client data.
        * @param {Object} data - Client, advisor, and authentication data payload.
        * @param {Function} localizeContent - Function used to localize UI content.
    */

    const clientAuthTitle = document.createElement('h3');
    clientAuthTitle.classList.add('client-auth-title');
    const clientNameLabel = document.createElement('span');
    clientNameLabel.setAttribute('data-i18n', 'client_name_label');
    clientAuthTitle.appendChild(clientNameLabel);
    clientAuthTitle.appendChild(document.createTextNode(`\u00a0${data.client_name}`));
    clientAuthDiv.appendChild(clientAuthTitle);

    const datailsTitles = document.createElement('div');
    datailsTitles.classList.add('titles');
    const addressTitle = document.createElement('div');
    addressTitle.classList.add('address-title');
    addressTitle.setAttribute('data-i18n', 'address');
    const authTitle = document.createElement('div');
    authTitle.classList.add('auth-title');
    authTitle.setAttribute('data-i18n', 'auth');
    datailsTitles.appendChild(addressTitle);
    datailsTitles.appendChild(authTitle);
    clientAuthDiv.appendChild(datailsTitles);

    const contentDiv = document.createElement('div');
    contentDiv.classList.add('content');

    // Client Details div
    const clientDetailsDiv = document.createElement('div');
    clientDetailsDiv.classList.add('client-details');
    const clientAddress = document.createElement('div');
    clientAddress.classList.add('address');
    clientAddress.textContent = `${data.client_address}`;
    const clientCity = document.createElement('div');
    clientCity.classList.add('city');
    clientCity.textContent = `${data.client_city}`;
    const clientEmail = document.createElement('div');
    clientEmail.classList.add('email');
    clientEmail.textContent = `${data.client_email}`;
    clientDetailsDiv.appendChild(clientAddress);
    clientDetailsDiv.appendChild(clientCity);
    clientDetailsDiv.appendChild(clientEmail);
    
    // Client Auth div
    const clientAuthDetailsDiv = document.createElement('div');
    clientAuthDetailsDiv.classList.add('client-auth');

    const boxesDiv = document.createElement('div');
    boxesDiv.classList.add('boxes');

    // Client Passkey Box
    const clientPasskeyBox = document.createElement('div');
    clientPasskeyBox.classList.add('passkey-box');
    const clientPasskeyInstruction = document.createElement('div');
    clientPasskeyInstruction.classList.add('instruction');
    clientPasskeyInstruction.setAttribute('data-i18n', 'passkey_advisor_from_client');
    clientPasskeyBox.appendChild(clientPasskeyInstruction);
    const clientPasskeyDiv = document.createElement('div');
    clientPasskeyDiv.classList.add('passkey');
    const clientPasskeySpan = document.createElement('span');
    clientPasskeySpan.id = 'client_passkey';
    clientPasskeySpan.classList.add('display-layer');
    clientPasskeySpan.textContent = data.client.user_passkey;
    clientPasskeyDiv.appendChild(clientPasskeySpan);
    clientPasskeyBox.appendChild(clientPasskeyDiv);
    boxesDiv.appendChild(clientPasskeyBox);

    // Advisor Passkey Box
    const advisorPasskeyBox = document.createElement('div');
    advisorPasskeyBox.classList.add('passkey-box');
    const advisorPasskeyInstruction = document.createElement('div');
    advisorPasskeyInstruction.classList.add('instruction');
    advisorPasskeyInstruction.setAttribute('data-i18n', 'passkey_advisor_to_client');
    advisorPasskeyBox.appendChild(advisorPasskeyInstruction);
    const advisorPasskeyDiv = document.createElement('div');
    advisorPasskeyDiv.classList.add('passkey');
    const advisorPasskeySpan = document.createElement('span');
    advisorPasskeySpan.id = 'advisor_client_passkey';
    advisorPasskeySpan.classList.add('display-layer');
    advisorPasskeySpan.textContent = data.advisor_client.advisor_passkey;
    advisorPasskeyDiv.appendChild(advisorPasskeySpan);
    advisorPasskeyBox.appendChild(advisorPasskeyDiv);
    boxesDiv.appendChild(advisorPasskeyBox);

    clientAuthDetailsDiv.appendChild(boxesDiv);

    // Timer
    const timerContainer = document.createElement('div');
    timerContainer.classList.add('timer-container');
    const timerDiv = document.createElement('div');
    timerDiv.classList.add('timer');
    const circleDiv = document.createElement('div');
    circleDiv.classList.add('circle');
    circleDiv.id = 'circle_client';
    timerDiv.appendChild(circleDiv);
    timerContainer.appendChild(timerDiv);

    contentDiv.appendChild(clientDetailsDiv);
    contentDiv.appendChild(clientAuthDetailsDiv);
    contentDiv.appendChild(timerContainer);
    
    clientAuthDiv.appendChild(contentDiv);

    localizeContent();
}
