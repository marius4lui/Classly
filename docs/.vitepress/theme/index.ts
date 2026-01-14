// Custom VitePress Theme with Copy Page Button
// https://vitepress.dev/guide/extending-default-theme

import DefaultTheme from 'vitepress/theme'
import { h } from 'vue'
import CopyPageButton from '../components/CopyPageButton.vue'
import './custom.css'

export default {
    extends: DefaultTheme,
    Layout() {
        return h(DefaultTheme.Layout, null, {
            // Add copy button to the aside outline (right sidebar)
            'aside-outline-after': () => h(CopyPageButton),
        })
    }
}
