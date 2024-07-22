export default class BaseHTMLElement extends HTMLElement {
    constructor(templateId, cssPath, isShadowDOM = false) {
        super();
        this.templateId = templateId;
        this.cssPath = cssPath;
        this.isShadowDOM = isShadowDOM;
        this.initializeRoot();
    }

    initializeRoot() {
        this.root = this.isShadowDOM ? this.attachShadow({ mode: 'open' }) : this;
    }

    async loadCSS(styles) {
        if (this.cssPath) {
            try {
                const request = await fetch(this.cssPath);
                const text = await request.text();
                styles.textContent = text;
            } catch (error) {
                console.error(`Failed to load CSS from ${this.cssPath}:`, error);
            }
        }
    }

    connectedCallback() {
        const styles = document.createElement('style');
        this.loadCSS(styles);
        this.root.appendChild(styles);

        const template = document.getElementById(this.templateId);
        if (template) {
            const content = template.content.cloneNode(true);
            this.root.appendChild(content);
        } else {
            console.error(`Template with ID ${this.templateId} not found.`);
        }
    }
}
