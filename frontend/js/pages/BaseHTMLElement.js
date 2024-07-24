export default class BaseHTMLElement extends HTMLElement {
    constructor(templateId) {
        super();
        this.templateId = templateId;
    }

    connectedCallback() {
        const template = document.getElementById(this.templateId);
        if (template) {
            const content = template.content.cloneNode(true);
            this.appendChild(content);
        } else {
            console.error(`Template with ID ${this.templateId} not found.`);
        }
    }
}
