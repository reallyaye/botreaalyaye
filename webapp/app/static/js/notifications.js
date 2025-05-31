// NOTIFICATIONS MODULE
function showNotification(msg, type) {
    let n = document.createElement('div');
    n.className = 'custom-toast ' + (type === 'success' ? 'toast-success' : 'toast-error');
    n.textContent = msg;
    document.body.appendChild(n);
    setTimeout(() => { n.classList.add('show'); }, 10);
    setTimeout(() => { n.classList.remove('show'); setTimeout(()=>n.remove(), 300); }, 2500);
}

export { showNotification };
