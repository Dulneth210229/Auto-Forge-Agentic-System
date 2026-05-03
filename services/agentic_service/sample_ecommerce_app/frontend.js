function renderProduct(userInput) {
    document.getElementById("product").innerHTML = userInput;
}

function saveToken(token) {
    localStorage.setItem("auth_token", token);
}

function runDangerous(input) {
    eval(input);
}

console.log("token", "abc123-secret-token");