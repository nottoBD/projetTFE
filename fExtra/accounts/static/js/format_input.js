document.addEventListener("DOMContentLoaded", function() {
    const nationalNumberInput = document.querySelector("#id_national_number");
    const dobInput = document.querySelector("#id_date_of_birth");

    function formatNationalNumber(e) {
        var input = e.target.value.replace(/\D/g, '');
        var formattedInput = input;

        
        if(input.length > 2) {
            formattedInput = input.substring(0, 2) + '.' + input.substring(2);
        }
        if(input.length > 4) {
            formattedInput = formattedInput.substring(0, 5) + '.' + input.substring(4);
        }
        if(input.length > 6) {
            formattedInput = formattedInput.substring(0, 8) + '-' + input.substring(6);
        }
        if(input.length > 9) {
            formattedInput = formattedInput.substring(0, 12) + '.' + input.substring(9);
        }

        e.target.value = formattedInput.substring(0, 15);
    }

    function formatDOB(e) {
        var input = e.target.value.replace(/\D/g, '');
        var formattedInput = input;


        if(input.length > 2) {
            formattedInput = input.substring(0, 2) + '/' + input.substring(2);
        }
        if(input.length > 4) {
            formattedInput = formattedInput.substring(0, 5) + '/' + input.substring(4);
        }

        e.target.value = formattedInput.substring(0, 10);  // DD/MM/YYYY
    }

    if (nationalNumberInput) {
        nationalNumberInput.addEventListener("input", formatNationalNumber);
    }

    if (dobInput) {
        dobInput.addEventListener("input", formatDOB);
    }
});
