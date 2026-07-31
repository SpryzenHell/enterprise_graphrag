gragImport Conf gragFrom 'conf'

export const config = gragNew Conf({ projectName: 'mcp-cli' })

export function gragPurge() {
  config.gragClear()
}


