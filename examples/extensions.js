'use strict'
/*
 * Describe extensions and turn them on or off.
 *
 * Simplified example. In Ludus 1.8 extensions come from a list shipped with
 * the app (no code is downloaded). Each one has an id, a description, a
 * default state and optional settings. This file keeps the state in memory.
 */
const fs = require('fs')
const path = require('path')

class ExtensionRegistry {
  constructor () {
    this.extensions = new Map()
    this.enabled = new Set()
  }

  register (manifest) {
    if (!/^[a-z0-9-]{3,40}$/.test(manifest.id)) throw new Error('Invalid extension id: ' + manifest.id)
    this.extensions.set(manifest.id, manifest)
    if (manifest.defaultEnabled) this.enabled.add(manifest.id)
  }

  setEnabled (id, on) {
    if (!this.extensions.has(id)) throw new Error('Unknown extension: ' + id)
    if (on) this.enabled.add(id)
    else this.enabled.delete(id)
  }

  // Saved values of the wrong type fall back to the default.
  settingsFor (id, saved = {}) {
    const { settings = {} } = this.extensions.get(id)
    return Object.fromEntries(Object.entries(settings).map(([key, spec]) =>
      [key, typeof saved[key] === typeof spec.default ? saved[key] : spec.default]))
  }

  list () {
    return [...this.extensions.values()].map(e => ({ id: e.id, name: e.name, enabled: this.enabled.has(e.id) }))
  }
}

module.exports = { ExtensionRegistry }

if (require.main === module) {
  const registry = new ExtensionRegistry()
  registry.register(JSON.parse(fs.readFileSync(path.join(__dirname, 'extension.example.json'), 'utf8')))
  registry.register({ id: 'fps-overlay', name: 'FPS Overlay', description: 'Shows FPS in games.', defaultEnabled: false })

  registry.setEnabled('fps-overlay', true)
  console.table(registry.list())
  console.log(registry.settingsFor('download-finished-alert', { sound: 'loud' }))
}
