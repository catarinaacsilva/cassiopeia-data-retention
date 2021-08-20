function handleSubmit(event) {
  event.preventDefault();
  const path = event.target.action
  console.log(path);
  const data = new FormData(event.target);
  const values = Object.fromEntries(data.entries());
  const body = JSON.stringify(values);
  console.log(values);

  let redirect_url = null;
  if ('redirect' in event.target) {
    redirect_url = event.target['redirect'].value;
  }
   
  console.log('redirect url: '+redirect_url);

  const xhr = new XMLHttpRequest();
  xhr.open("POST", path, true);
  xhr.setRequestHeader('Content-Type', 'application/json');
  xhr.timeout = 1000;

  xhr.ontimeout = function () {
    alert('Error('+xhr.status+'): '+xhr.statusText);
    console.error('The request for ' + path + ' timed out.');
  };
  
  xhr.onload = function () {
    if (xhr.readyState == 4) {
      if (parseInt(xhr.status/100) == 2) {
        console.log('OK:'+xhr.status);
        if (redirect_url != null) {window.location.assign(redirect_url);}
      } else {
        alert('Error('+xhr.status+'): '+xhr.statusText);
        console.error(xhr.statusText);
      }
    }
  };

  xhr.send(body);
}

console.log('Register all forms....')
const forms = document.getElementsByTagName('form');
for (let i = 0; i < forms.length; i++) {
  forms[i].addEventListener('submit', handleSubmit);
}