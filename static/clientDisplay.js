// Display customer data in the advisor interface function
export const clientDisplay = (clientAuthDiv, data, localizeContent) => {

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

  // Client Password Box
  const clientPwdBox = document.createElement('div');
  clientPwdBox.classList.add('password-box');
  const clientPwdInstruction = document.createElement('div');
  clientPwdInstruction.classList.add('instruction');
  clientPwdInstruction.setAttribute('data-i18n', 'password_advisor_from_client');
  clientPwdBox.appendChild(clientPwdInstruction);
  const clientPwdDiv = document.createElement('div');
  clientPwdDiv.classList.add('password');
  const clientPwdSpan = document.createElement('span');
  clientPwdSpan.id = 'client_pwd';
  clientPwdSpan.classList.add('display-layer');
  clientPwdSpan.textContent = data.client.user_pwd;
  clientPwdDiv.appendChild(clientPwdSpan);
  clientPwdBox.appendChild(clientPwdDiv);
  boxesDiv.appendChild(clientPwdBox);

  // Advisor Password Box
  const advisorPwdBox = document.createElement('div');
  advisorPwdBox.classList.add('password-box');
  const advisorPwdInstruction = document.createElement('div');
  advisorPwdInstruction.classList.add('instruction');
  advisorPwdInstruction.setAttribute('data-i18n', 'password_advisor_to_client');
  advisorPwdBox.appendChild(advisorPwdInstruction);
  const advisorPwdDiv = document.createElement('div');
  advisorPwdDiv.classList.add('password');
  const advisorPwdSpan = document.createElement('span');
  advisorPwdSpan.id = 'advisor_client_pwd';
  advisorPwdSpan.classList.add('display-layer');
  advisorPwdSpan.textContent = data.advisor_client.advisor_pwd;
  advisorPwdDiv.appendChild(advisorPwdSpan);
  advisorPwdBox.appendChild(advisorPwdDiv);
  boxesDiv.appendChild(advisorPwdBox);

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
