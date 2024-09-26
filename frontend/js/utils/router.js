const Router = {
    init: async () => {
        app.isLoggedIn = await Router.checkIsLoggedIn();

        Router.go(location.pathname);

        // This perhaps will get modified for the Auth conditions
        window.addEventListener('popstate', event => {
            Router.go(event.state ? event.state.router : "/", false);
        });
    },

    go: (router, addToHistory = true) => {
        if (addToHistory) {
            window.history.pushState({ router }, null, router);
        }

        // render the pages
        // this could be refactored and scaled later
        switch (router) {
            case "/":
                Router.loadMainHomeContent('game-page');
                break;
            case "/profile":
                Router.loadMainHomeContent('profile-page');
                break;
            case "/chat":
                Router.loadMainHomeContent('chat-page');
                break;
            case "/leaderboard":
                Router.loadMainHomeContent('leaderboard-page');
                break;
            case "/settings":
                Router.loadMainHomeContent('settings-page');
                break;
            case "/login":
                Router.loadSignAndLoginPage('login-page');
                break;
            case "/signup":
                Router.loadSignAndLoginPage('signup-page');
                break;
            default:
                Router.loadNotFoundPage('not-found-page');
        }
    },

    checkIsLoggedIn: async () => {
        // Check if the user is logged in
        app.profile = await app.api.getProfile();

        if (app.profile) {
            return true;
        }

        return false;
    },

    loadMainHomeContent: (pageName) => {
        // If the user is not logged in go to login page
        if (!app.isLoggedIn) {
            app.router.go("/login");
            return;
        }

        // If the home page doesn't exist in the DOM then render the home page first
        if (!document.querySelector('home-page')) {
            Router.loadHomePage();
        }
        
        const mainElement = document.querySelector('main')

        // If the page content already exists, no need to render it again (for performance reasons)
        if (mainElement.querySelector(pageName)) return;

        // Load the new page on the main content
        const mainContent = document.createElement(pageName)
        mainElement.innerHTML = ''
        mainElement.appendChild(mainContent)
    },

    loadHomePage: () => {
        // Delete home, login, sign up or 404 pages if they exist then load the home page
        Router.removeOldPages();
        Router.insertPage('home-page');
    },

    loadSignAndLoginPage: (pageName) => {
        // Delete home, login, sign up or 404 pages if they exist then load the sign up or login page
        Router.removeOldPages();

        if (app.isLoggedIn) {
            app.router.go("/");
            return;
        }

        Router.insertPage(pageName);
    },

    loadNotFoundPage: () => {
        // Delete home, login, sign up or 404 pages if they exist then load the 404 page
        Router.removeOldPages();
        Router.insertPage('not-found-page');
    },

    // Insert the page to the body
    insertPage: (pageName) => {
        const newElement = document.createElement(pageName);
        const bootstrapScript = document.querySelector('body > script:last-of-type'); // Insert the pages before bootstrap js bundle script

        if (bootstrapScript) {
            document.body.insertBefore(newElement, bootstrapScript);
        } else {
            document.body.appendChild(newElement);
        }
    },

    removeOldPages: () => {
        // Remove old pages if they exist
        const oldPages = ['home-page', 'login-page', 'signup-page', 'not-found-page'];

        oldPages.forEach(page => {
            const pageElement = document.querySelector(page);
            if (pageElement) pageElement.remove();
        });
    },
}

export default Router;
