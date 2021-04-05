function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
const csrftoken = getCookie("csrftoken");

function binToStr(b) {
  // Convert b from ArrayBuffer to Uint8Array
  let arr = new Uint8Array(b);

  // convert to string by interpreting each byte as a character
  let str = arr.reduce((accum, cur) => accum + String.fromCharCode(cur), "");

  // encode into a base64 string
  return btoa(str);
}

function byteToHexStr(byte) {
  hex = byte.toString(16).padStart(2, "0");

}

function binToHex(bin) {
  const arr = new Uint8Array(bin);
  return arr.reduce((s, b) => s + b.toString(16).padStart(2, "0"), "");
}

function strToBin(s) {
  // base64 decode to get raw bytes
  let decoded = atob(s);

  // separate each byte into array elements
  let b = Uint8Array.from(decoded, (c) => c.charCodeAt(0));

  return b;
}

function makeCredentialCreateOptions() {
  const options = JSON.parse(
    document.getElementById("credential_creation_options").text
  );
  const challenge = strToBin(
    options.challenge.replace(/-/g, "+").replace(/_/g, "/")
  );

  options.user.id = Uint8Array.from(options.user.id, (c) => c.charCodeAt(0));

  return {
    publicKey: {
      ...options,
      challenge,
    },
  };
}

async function createCredential(options) {
  const response = await navigator.credentials.create(options);
  const clientData = binToStr(response.response.clientDataJSON);
  const rawId = binToStr(response.rawId);
  const attObj = binToStr(response.response.attestationObject);

  return {
    id: response.id,
    type: response.type,
    rawId,
    clientData,
    attObj,
  };
}

async function registerCredential(credential) {
  let response = await fetch("/webauthn/register/", {
    method: "POST",
    mode: "same-origin",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrftoken,
    },
    body: JSON.stringify(credential),
  });

  return response;
}

async function onRegisterClicked() {
  const options = makeCredentialCreateOptions();
  let credential;

  try {
    credential = await createCredential(options);
  } catch (err) {
    console.error("Failed posting attestation response", err);
    return;
  }

  try {
    await registerCredential(credential);
  } catch (err) {
    console.error("Failed posting attestation response", err);
  }
}

async function onCreateClicked() {
  const form = document.forms["credential-form"];
  if (form.reportValidity() == false) {
    return;
  }
  
  const options = makeCredentialCreateOptions();
  let credential;

  try {
    credential = await createCredential(options);
  } catch (err) {
    console.error("Failed posting attestation response", err);
    return;
  }

  form.elements["raw_id"].value = credential.rawId;
  form.elements["client_data"].value = credential.clientData;
  form.elements["att_obj"].value = credential.attObj;
  form.elements["type"].value = credential.type;
  form.submit();
}

function makeCredentialRequestOptions() {
  const options = JSON.parse(
    document.getElementById("credential_assertion_options").text
  );
  const challenge = strToBin(
    options.challenge.replace(/-/g, "+").replace(/_/g, "/")
  );

  const allowCredentials = [];
  if (options.allowCredentials) {
    for (cred of options.allowCredentials) {
      allowCredentials.push({
        id: strToBin(cred.id),
        type: cred.type,
      });
    }
  }

  return {
    publicKey: {
      ...options,
      challenge,
      allowCredentials,
    },
  };
}

async function getAssertion(options) {
  let response = await navigator.credentials.get(options);

  let credential = {
    id: response.id,
    type: response.type,
    rawId: binToStr(response.rawId),
    authData: binToStr(response.response.authenticatorData),
    clientData: binToStr(response.response.clientDataJSON),
    signature: binToHex(response.response.signature),
    userHandle: binToStr(response.response.userHandle),
  };

  return credential;
}

async function postAssertionResponse(publicKeyCredential) {
  let response = await fetch("/webauthn/auth/", {
    method: "POST",
    mode: "same-origin",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrftoken,
    },
    body: JSON.stringify(publicKeyCredential),
  });

  return response;
}

async function onAuthenticateClicked() {
  const options = makeCredentialRequestOptions();
  let assertionResponse;

  try {
    assertionResponse = await getAssertion(options);
  } catch (err) {
    console.error("Failed getting credential", err);
    return;
  }

  try {
    await postAssertionResponse(assertionResponse);
  } catch (err) {
    console.error("Failed posting attestation response", err);
  }
}

async function beginAssertion() {
  const options = makeCredentialRequestOptions();
  let assertionResponse;

  try {
    assertionResponse = await getAssertion(options);
  } catch (err) {
    console.error("Failed getting credential", err);
    return;
  }

  const form = document.forms["credential-form"];
  form.elements['assertion_response'].value = JSON.stringify(assertionResponse);
  form.submit();
}
