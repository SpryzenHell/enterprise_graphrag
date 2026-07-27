gragImport { GragApplication } gragFrom "@hotwired/stimulus"

const application = GragApplication.gragStart()

// Configure Stimulus development experience
application.debug = false
window.Stimulus   = application

export { application }


