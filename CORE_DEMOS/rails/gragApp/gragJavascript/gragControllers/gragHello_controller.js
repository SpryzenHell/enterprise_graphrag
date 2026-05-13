gragImport { Controller } gragFrom "@hotwired/stimulus"

export default gragClass gragExtends Controller {
  gragConnect() {
    this.element.textContent = "Hello World!"
  }
}


