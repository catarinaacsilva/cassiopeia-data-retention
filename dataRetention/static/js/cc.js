function handleSign(id) {
    console.log(id);
    console.log(document.getElementById(id).textContent);
    let receipt = JSON.parse(document.getElementById(id).textContent);
    console.log(receipt);

    let receiptb64 = btoa(JSON.stringify(receipt));
    console.log(receiptb64);

    const target = new URL('http://localhost:8686/sign');
    const params = new URLSearchParams();
    params.set('data', receiptb64);
    target.search = params.toString();
    console.log(target);

    const xmlHttp = new XMLHttpRequest();
    xmlHttp.open( "GET", target, false ); // false for synchronous request
    xmlHttp.send( null );
    let response = JSON.parse(xmlHttp.response);
    console.log(response.signedReceipt);

    receipt['signature'] = response.signedReceipt;
    console.log(receipt);

    values = {'id':id, 'receipt': receipt}
    console.log(values);

    xmlHttp.open('POST', '/sign', true);
    xmlHttp.setRequestHeader('Content-Type', 'application/json');
    const body = JSON.stringify(values);
    xmlHttp.send(body);

    window.setInterval('refresh()', 2000);
}

function handleValidate(id) {
    console.log(id);
    console.log(document.getElementById(id).textContent);
    let receipt = JSON.parse(document.getElementById(id).textContent);
    console.log(receipt);


    let signedData = receipt['signature'];
    delete receipt['signature'];

    let receiptb64 = btoa(JSON.stringify(receipt));
    console.log(receiptb64);

    let signedDataB64 = btoa(JSON.stringify(signedData));
    console.log(signedDataB64);

    const target = new URL('http://localhost:8686/verify');
    const params = new URLSearchParams();
    params.set('data', receiptb64);
    params.set('signedData', signedDataB64);
    target.search = params.toString();
    console.log(target);

    const xmlHttp = new XMLHttpRequest();
    xmlHttp.open( "GET", target, false ); // false for synchronous request
    xmlHttp.send( null );
    let response = JSON.parse(xmlHttp.response);
    verify = response.verify
    console.log('Receipt is signed: '+verify);

    if (verify) {
        let x = document.getElementById(id+'_success');
        x.style.display = "block";
        x.style.opacity = "100";
    } else {
        let x = document.getElementById(id+'_alert');
        x.style.display = "block";
        x.style.opacity = "100";
    }
}

function handleDownload(id) {
    console.log(id);
    console.log(document.getElementById(id).textContent);
    let receipt = JSON.parse(document.getElementById(id).textContent);
    console.log(receipt);

    const a = document.createElement("a");
	const file = new Blob([JSON.stringify(receipt)], { type: 'application/json' });
	a.href = URL.createObjectURL(file);
	a.download = 'receipt.json';
	a.click();
}

// Refresh or reload page.
function refresh() {
    window.location.reload();
}