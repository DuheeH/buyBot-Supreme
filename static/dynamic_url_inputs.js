// Dynamically generates url inputs an Item labels
    document.addEventListener('DOMContentLoaded', function() {
        var formfield = document.getElementById('formfield');
        var inputCount = 2; // Initialize the input count

        function addInput() {
            var inputContainer = document.createElement('div');
            inputContainer.className = 'input-container';

            var label = document.createElement('label');
            label.textContent = 'Item ' + inputCount + ':';
            label.setAttribute('for', 'url');
            label.setAttribute('class', 'label')

            var newUrl = document.createElement('input');
            newUrl.setAttribute('autocomplete','off');
            newUrl.setAttribute('required','');
            newUrl.setAttribute('class','form-control mx-auto w-auto');
            newUrl.setAttribute('name','url');
            newUrl.setAttribute('id','url');
            newUrl.setAttribute('placeholder','URL');
            newUrl.setAttribute('type','text');

            inputContainer.appendChild(label);
            inputContainer.appendChild(newUrl);
            formfield.appendChild(inputContainer);

            inputCount++; // Increment the input count
        }

        function removeInput() {
            var inputContainers = formfield.querySelectorAll('.input-container');
            if(inputContainers.length > 1) {
                formfield.removeChild(inputContainers[inputContainers.length - 1]);
                inputCount--; // Decrement the input count
            }
        }

        document.querySelector("#add").addEventListener('click', function(event) {
            addInput();
        });

        document.querySelector("#remove").addEventListener('click', function(event) {
            removeInput();
        });
    });