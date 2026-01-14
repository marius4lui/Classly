<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useData, useRoute } from 'vitepress'

const copied = ref(false)
const route = useRoute()

async function copyPageAsMarkdown() {
  try {
    // Get the current page path
    const pagePath = route.path
    
    // Fetch the raw markdown file
    let mdPath = pagePath === '/' ? '/index.md' : `${pagePath}.md`
    if (pagePath.endsWith('/')) {
      mdPath = `${pagePath}index.md`
    }
    
    const response = await fetch(mdPath)
    
    if (response.ok) {
      const markdown = await response.text()
      await navigator.clipboard.writeText(markdown)
      copied.value = true
      setTimeout(() => copied.value = false, 2000)
    } else {
      // Fallback: copy page content as text
      const content = document.querySelector('.vp-doc')?.textContent || ''
      await navigator.clipboard.writeText(content)
      copied.value = true
      setTimeout(() => copied.value = false, 2000)
    }
  } catch (err) {
    console.error('Failed to copy:', err)
    // Fallback: copy rendered content
    const content = document.querySelector('.vp-doc')?.textContent || ''
    await navigator.clipboard.writeText(content)
    copied.value = true
    setTimeout(() => copied.value = false, 2000)
  }
}
</script>

<template>
  <button 
    class="copy-page-btn"
    @click="copyPageAsMarkdown"
    :title="copied ? 'Kopiert!' : 'Seite als Markdown kopieren'"
  >
    <span v-if="copied" class="icon">✓</span>
    <span v-else class="icon">📋</span>
    <span class="label">{{ copied ? 'Kopiert!' : 'Als MD kopieren' }}</span>
  </button>
</template>

<style scoped>
.copy-page-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  font-size: 13px;
  font-weight: 500;
  color: var(--vp-c-text-2);
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-divider);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.copy-page-btn:hover {
  color: var(--vp-c-brand-1);
  border-color: var(--vp-c-brand-1);
  background: var(--vp-c-bg-soft);
}

.icon {
  font-size: 14px;
}

.label {
  white-space: nowrap;
}

@media (max-width: 640px) {
  .label {
    display: none;
  }
  .copy-page-btn {
    padding: 8px 10px;
  }
}
</style>
