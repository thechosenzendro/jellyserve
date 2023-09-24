import path from "path"
import fs from "fs/promises"
import fsSync from "fs"
import { rollup } from "rollup"
import chokidar from "chokidar"
import svelte from "rollup-plugin-svelte"
import resolve from "@rollup/plugin-node-resolve"

const FRONTEND_PATH = "./"
const RUNTIME_PATH = "../public/.runtime"
const TEMPLATES_PATH = "./.templates"

const watcher = chokidar.watch(FRONTEND_PATH, {
    persistent: true
})

if (!fsSync.existsSync(RUNTIME_PATH)) {
    await fs.mkdir(RUNTIME_PATH)
}

watcher.on("add", async (_path) => {
    if (_path.includes(".svelte")) {
        const componentName = path.basename(_path, ".svelte")
        const COMPONENT_PATH = `${RUNTIME_PATH}/${componentName}`

        if (!fsSync.existsSync(COMPONENT_PATH)) {
            await fs.mkdir(COMPONENT_PATH)
        }

        const componentTemplate = (await fs.readFile(`${TEMPLATES_PATH}/template.js`)).toString()

        await fs.writeFile(`${COMPONENT_PATH}/component.js`, componentTemplate.replace("$component_code", escapeBackslash(path.resolve(_path))))
        console.log(`Component ${componentName} was created.`)
        await generateComponent(componentName, COMPONENT_PATH)

    }
})

watcher.on("change", async (_path) => {
    if (_path.includes(".svelte")) {
        const componentName = path.basename(_path, ".svelte")
        const COMPONENT_PATH = `${RUNTIME_PATH}/${componentName}`
        console.log(`Component ${componentName} was changed.`)
        await generateComponent(componentName, COMPONENT_PATH)
    }
})

watcher.on("unlink", async (_path) => {
    if (_path.includes(".svelte")) {
        const componentName = path.basename(_path, ".svelte")
        const COMPONENT_PATH = `${RUNTIME_PATH}/${componentName}`
        console.log(`Component ${componentName} was deleted.`)
        await fs.rm(COMPONENT_PATH, { recursive: true, force: true })
    }
})

process.on("SIGINT", async (signal) => {
    console.log(`Cleaning up before exiting...`)
    await fs.rm(RUNTIME_PATH, { recursive: true, force: true })
    process.exit(0);
});


async function generateComponent(name, COMPONENT_PATH) {
    console.log(`Generating component ${name}...`)
    let thrown = false
    try {
        const bundle = await rollup({
            input: `${COMPONENT_PATH}/component.js`,
            plugins: [
                svelte({
                    include: `${FRONTEND_PATH}/**/*.svelte`,
                    emitCss: false
                }),
                resolve({ browser: true })
            ],
        })
        bundle.write({
            file: `${COMPONENT_PATH}/bundle.js`,
            format: 'iife',
            name: 'app',

        })
    }
    catch (err) {
        thrown = true
        console.log(`Svelte Generation Error: ${err}`)
    }
    finally {
        if (!thrown) {
            console.log(`Component ${name} generated successfully.`)
        }
        else {
            console.log(`Component ${name} generated with errors.`)
        }
    }
}

function escapeBackslash(string) {
    return string.replaceAll("\\", "/")
}