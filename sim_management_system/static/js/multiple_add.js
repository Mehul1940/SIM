function addInput(containerId, inputName) {
  const container = document.getElementById(containerId);
  const inputGroup = document.createElement('div');
  inputGroup.className = 'input-group mb-2';

  const newInput = document.createElement('input');
  newInput.type = 'text';
  newInput.name = inputName;
  newInput.className = 'form-control';
  newInput.placeholder = 'Enter ' + inputName.replace('[]', '').replace('_', ' ');

  const removeBtn = document.createElement('button');
  removeBtn.type = 'button';
  removeBtn.className = 'btn btn-outline-danger';
  removeBtn.innerHTML = '<i class="fas fa-trash"></i>';
  removeBtn.onclick = function() {
    inputGroup.remove();
  };

  inputGroup.appendChild(newInput);
  inputGroup.appendChild(removeBtn);
  container.appendChild(inputGroup);
}

function removeInput(button) {
  const inputGroup = button.parentElement;
  inputGroup.remove();
}