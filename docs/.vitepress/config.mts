import { defineConfig } from 'vitepress'

// https://vitepress.dev/reference/site-config
export default defineConfig({
    title: "Classly",
    description: "Der einfachste Weg, deine Klasse zu organisieren.",
    lang: 'de-DE',
    // base: '/Classly/', // Removed for custom domain docs.classly.site

    themeConfig: {
        // https://vitepress.dev/reference/default-theme-config
        nav: [
            { text: 'Home', link: '/' },
            { text: 'Guide', link: '/user-guide/getting-started' },
            { text: 'Setup', link: '/setup/installation' },
            { text: 'Entwicklung', link: '/development/contributing' }
        ],

        sidebar: {
            '/setup/': [
                {
                    text: 'Einrichtung & Hosting',
                    items: [
                        { text: 'Installation', link: '/setup/installation' },
                        { text: 'Konfiguration', link: '/setup/configuration' }
                    ]
                }
            ],
            '/user-guide/': [
                {
                    text: 'Benutzerhandbuch',
                    items: [
                        { text: 'Erste Schritte', link: '/user-guide/getting-started' },
                        { text: 'Funktionen & Rollen', link: '/user-guide/features' }
                    ]
                }
            ],
            '/development/': [
                {
                    text: 'Entwicklung',
                    items: [
                        { text: 'Mitmachen', link: '/development/contributing' }
                    ]
                }
            ]
        },

        socialLinks: [
            { icon: 'github', link: 'https://github.com/marius4lui/Classly' }
        ],

        footer: {
            message: 'Released under the MIT License.',
            copyright: 'Copyright © 2024-present Classly'
        },

        search: {
            provider: 'local'
        },

        editLink: {
            pattern: 'https://github.com/marius4lui/Classly/edit/main/docs/:path',
            text: 'Diese Seite auf GitHub bearbeiten'
        }
    }
})
