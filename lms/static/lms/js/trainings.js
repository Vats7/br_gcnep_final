console.log('trainings.js')


const alertBox = document.getElementById('alert-box')





const handleAlerts = (type, msg) => {
    alertBox.innerHTML = `
        <div class="alert alert-${type}" role="alert">
          ${msg}
        </div>
    `
}