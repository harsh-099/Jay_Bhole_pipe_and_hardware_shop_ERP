// -------------------------------
// Show / Hide Password
// -------------------------------

const togglePassword = document.getElementById("togglePassword");
const passwordInput = document.getElementById("password");

if (togglePassword && passwordInput) {

    togglePassword.addEventListener("click", function () {

        if (passwordInput.type === "password") {

            passwordInput.type = "text";

            this.innerHTML =
                '<i class="fa fa-eye-slash"></i>';

        } else {

            passwordInput.type = "password";

            this.innerHTML =
                '<i class="fa fa-eye"></i>';

        }

    });

}

// -------------------------------
// Remember Username
// -------------------------------

const username = document.querySelector(
    "input[name='username']"
);

const remember = document.querySelector(
    "input[name='remember']"
);

if (localStorage.getItem("remember_username")) {

    username.value = localStorage.getItem(
        "remember_username"
    );

    remember.checked = true;

}

document.querySelector("form").addEventListener(
    "submit",
    function () {

        if (remember.checked) {

            localStorage.setItem(

                "remember_username",

                username.value

            );

        } else {

            localStorage.removeItem(

                "remember_username"

            );

        }

    }
);

// -------------------------------
// Button Loading Effect
// -------------------------------

const form = document.querySelector("form");

const loginButton = document.querySelector(".login-btn");

form.addEventListener("submit", function () {

    loginButton.disabled = true;

    loginButton.innerHTML =

        '<span class="spinner-border spinner-border-sm me-2"></span>Signing In...';

});

// -------------------------------
// Input Animation
// -------------------------------

document.querySelectorAll(".form-control").forEach(

    function (input) {

        input.addEventListener(

            "focus",

            function () {

                this.parentElement.style.transform =
                    "scale(1.02)";

                this.parentElement.style.transition =
                    ".2s";

            }

        );

        input.addEventListener(

            "blur",

            function () {

                this.parentElement.style.transform =
                    "scale(1)";

            }

        );

    }

);

// -------------------------------
// Enter Key
// -------------------------------

document.addEventListener(

    "keypress",

    function (e) {

        if (e.key === "Enter") {

            form.submit();

        }

    }

);
