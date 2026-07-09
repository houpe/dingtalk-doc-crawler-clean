import { createServer } from 'vitepress'
import { resolve } from 'path'

const root = resolve(process.cwd(), 'docs')
const server = await createServer(root, { port: 4001 })
await server.listen()
server.printUrls()
