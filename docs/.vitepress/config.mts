import { defineConfig } from 'vitepress'

// https://vitepress.dev/reference/site-config
export default defineConfig({
    title: "Classly",
    description: "Der einfachste Weg, deine Klasse zu organisieren.",
    lang: 'de-DE',
    // base: '/Classly/', // Removed for custom domain docs.classly.site

    markdown: {
        // Enable copy button for code blocks
        codeCopyButtonTitle: 'Code kopieren',
        // Enable line numbers for code blocks (optional)
        lineNumbers: false,
        // Code block container settings
        container: {
            tipLabel: 'Tipp',
            warningLabel: 'Warnung',
            dangerLabel: 'Achtung',
            infoLabel: 'Info',
            detailsLabel: 'Details'
        }
    },

    themeConfig: {
        // https://vitepress.dev/reference/default-theme-config
        nav: [
            { text: 'Home', link: '/' },
            { text: 'Funktionen', link: '/features/' },
            { text: 'Guide', link: '/user-guide/getting-started' },
            { text: 'API Docs', link: '/development/api' },
            { text: 'Status', link: 'https://info.classly.site/status/classly-info' },
            { text: 'Setup', link: '/setup/installation' },
            {
                text: 'Versionen',
                items: [
                    { text: 'v1.0.2', link: '/versions/v1.0.2/' },
                    { text: 'v1.0.1', link: '/versions/v1.0.1/' },
                    { text: 'v1', link: '/versions/v1/' }
                ]
            }
        ],

        sidebar: {
            '/features/': [
                {
                    text: 'Funktionen',
                    items: [
                        { text: 'Übersicht', link: '/features/' },
                        { text: '📅 Kalender & Events', link: '/features/calendar' },
                        { text: '👥 Rollen & Rechte', link: '/features/roles' },
                        { text: '🔑 Zugang & Logins', link: '/features/access' },
                        { text: '📱 Handy & App', link: '/features/mobile' }
                    ]
                }
            ],
            '/setup/': [
                {
                    text: 'Einrichtung & Hosting',
                    items: [
                        { text: 'Installation', link: '/setup/installation' },
                        { text: 'Installation (Legacy)', link: '/setup/installation-legacy' },
                        { text: 'Konfiguration', link: '/setup/configuration' },
                        { text: 'Setup Mini CLI', link: '/setup/mini-cli' }
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
                },
                {
                    text: 'API Dokumentation',
                    items: [
                        { text: '🔌 Übersicht', link: '/development/api' },
                        { text: '🔑 API v1', link: '/development/api-v1' },
                        { text: '📱 Legacy API', link: '/development/api-legacy' },
                        { text: '🔐 OAuth 2.0', link: '/development/api-oauth' },
                        { text: '🤖 AI-Integration', link: '/development/api-integration' }
                    ]
                }
            ],
            '/versions/': [
                {
                    text: 'Versionen',
                    items: [
                        { text: 'v1.0.2', link: '/versions/v1.0.2/' },
                        { text: 'v1.0.1', link: '/versions/v1.0.1/' },
                        { text: 'v1', link: '/versions/v1/' }
                    ]
                }
            ]
        },

        socialLinks: [
            { icon: 'github', link: 'https://github.com/marius4lui/Classly' }
        ],

        footer: {
            message: 'Dual-Licensed: Community License (non-commercial) or Commercial License. See <a href="https://github.com/marius4lui/Classly/blob/main/LICENSE">LICENSE</a> and <a href="https://github.com/marius4lui/Classly/blob/main/COMMERCIAL.md">COMMERCIAL.md</a>',
            copyright: 'Copyright © 2026-present Classly'
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
