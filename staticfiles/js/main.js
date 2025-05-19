function togglePwd(id, btn) {
    const input = document.getElementById(id);
    if (input.type === "password") {
        input.type = "text";
        btn.innerHTML = '<i class="fi fi-br-eye-crossed"></i>';
    } else {
        input.type = "password";
        btn.innerHTML = '<i class="fi fi-br-eye"></i>';
    }
}