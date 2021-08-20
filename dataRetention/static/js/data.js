function handleExport(id) {
    console.log(id);
    const base = window.location.protocol + '//' + window.location.hostname + ':' + window.location.port
    console.log(base);
    const target = new URL('/exportCsv/', base);
    const params = new URLSearchParams();
    params.set('stay_id', id);
    target.search = params.toString();
    console.log(target);

    const xhr = new XMLHttpRequest();
    xhr.open("GET", target, true);

    xhr.onload = function () {
        if (xhr.readyState == 4) {
            if (parseInt(xhr.status / 100) == 2) {
                console.log('OK:' + xhr.status);
                console.log(xhr.response);
                const a = document.createElement("a");
                const file = new Blob([xhr.response], { type: 'text/csv' });
                a.href = URL.createObjectURL(file);
                a.download = 'data.csv';
                a.click();
                //if (redirect_url != null) {window.location.assign(redirect_url);}
            } else {
                //alert('Error('+xhr.status+'): '+xhr.statusText);
                console.error(xhr.statusText);
            }
        }
    };

    xhr.send(null);
}

function handleDelete(id, email) {
    console.log(id+' '+email);

    const base = window.location.protocol + '//' + window.location.hostname + ':' + window.location.port
    console.log(base);
    const target = new URL('/removeDataUser/', base);
    const params = new URLSearchParams();
    params.set('stay_id', id);
    params.set('email', email);
    target.search = params.toString();
    console.log(target);

    const xhr = new XMLHttpRequest();
    xhr.open("DELETE", target, true);

    xhr.onload = function () {
        if (xhr.readyState == 4) {
            if (parseInt(xhr.status / 100) == 2) {
                console.log('OK:' + xhr.status);
                window.location.reload();
            } else {
                console.error(xhr.statusText);
            }
        }
    };

    xhr.send(null);
}