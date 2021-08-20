function handleSubmit(event) {
    event.preventDefault();
    const path=document.getElementById('form').action
    console.log(path);
    const data = new FormData(event.target);
    const values = Object.fromEntries(data.entries());
    console.log(values);
    const xhr = new XMLHttpRequest();
    xhr.open("POST", path, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    const body = JSON.stringify(values);
    xhr.send(body);
  }

  const form = document.querySelector('form');
  form.addEventListener('submit', handleSubmit);

