console.log('questions.js')


;(function () {
  const modal = new bootstrap.Modal(document.getElementById("addQuestionModal"))

  htmx.on("htmx:afterSwap", (e) => {
    // Response targeting #dialog => show the modal
    if (e.detail.target.id == "dialog") {
      modal.show()
    }
  })

  htmx.on("htmx:beforeSwap", (e) => {
    // Empty response targeting #dialog => hide the modal
    if (e.detail.target.id == "dialog" && !e.detail.xhr.response) {
      modal.hide()
      e.detail.shouldSwap = false
    }
  })

  // Remove dialog content after hiding
  htmx.on("hidden.bs.modal", () => {
    document.getElementById("dialog").innerHTML = ""
  })
})()


;(function () {
  const modal = new bootstrap.Modal(document.getElementById("addBulkQuestionModal"))

  htmx.on("htmx:afterSwap", (e) => {
    // Response targeting #dialog => show the modal
    if (e.detail.target.id == "dialogBulk") {
      modal.show()
    }
  })

  htmx.on("htmx:beforeSwap", (e) => {
    // Empty response targeting #dialog => hide the modal
    if (e.detail.target.id == "dialogBulk" && !e.detail.xhr.response) {
      modal.hide()
      e.detail.shouldSwap = false
    }
  })

  // // Remove dialog content after hiding
  // htmx.on("hidden.bs.modal", () => {
  //   document.getElementById("dialogBulk").innerHTML = ""
  // })
})()