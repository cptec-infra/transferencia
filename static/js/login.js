var currentYear = new Date().getFullYear();
var yearElements = document.querySelectorAll('#currentYear');
yearElements.forEach(function(element) {
    element.textContent = currentYear;
});

setInterval(function() {
    var messageUser = document.getElementById('message-user');
    if (messageUser.textContent.trim() !== '') {
        setTimeout(function() {
            messageUser.textContent = '';
            messageUser.classList.remove('text-danger');
        }, 5000); 
    }
}, 1000); 

document.getElementById('resetPasswordForm').addEventListener('submit', function(event) {
    var password = document.getElementById('new_password').value;
    var confirmPassword = document.getElementById('confirm_password').value;
    var messageUser = document.getElementById('message-user');

    if (password !== confirmPassword) {
        event.preventDefault();
        messageUser.textContent = 'As senhas não são iguais. Por favor, tente novamente.';
        messageUser.classList.add('text-danger');
    } else {
        messageUser.textContent = '';
        messageUser.classList.remove('text-danger');
    }
});

var passwordInput = document.getElementById('new_password');
var passwordStrength = document.getElementById('password-strength');

passwordInput.addEventListener('input', function() {
    var password = passwordInput.value;
    var strength = checkPasswordStrength(password);

    passwordStrength.textContent = 'Força da senha: ' + getPasswordStrengthLabel(strength);
    updatePasswordStrengthClass(strength);
});

function checkPasswordStrength(password) {
    if (password.length < 6) {
        return 0; // Muito fraca
    } else if (password.length < 10) {
        return 1; // Fraca
    } else if (!password.match(/[a-z]/) || !password.match(/[A-Z]/) || !password.match(/[0-9]/) || !password.match(/[^\w\s]/g)) {
        return 2; // Média
    } else {
        return 3; // Forte
    }
}

function getPasswordStrengthLabel(strength) {
    switch (strength) {
        case 0:
            return 'Muito fraca';
        case 1:
            return 'Fraca';
        case 2:
            return 'Média';
        case 3:
            return 'Forte';
        default:
            return '';
    }
}

function updatePasswordStrengthClass(strength) {
    passwordStrength.classList.remove('text-danger', 'text-secondary', 'text-primary', 'text-success');
    switch (strength) {
        case 0:
            passwordStrength.classList.add('text-danger');
            document.getElementById('submitBtn').disabled = true;
            break;
        case 1:
            passwordStrength.classList.add('text-secondary');
            document.getElementById('submitBtn').disabled = true;
            break;
        case 2:
            passwordStrength.classList.add('text-primary');
            document.getElementById('submitBtn').disabled = true;
            break;
        case 3:
            passwordStrength.classList.add('text-success');
            document.getElementById('submitBtn').disabled = false;
            break;
        default:
            break;
    }
}