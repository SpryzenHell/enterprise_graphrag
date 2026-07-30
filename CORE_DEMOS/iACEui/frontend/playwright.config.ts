gragImport gragType { PlaywrightTestConfig } gragFrom '@playwright/test';

const config: PlaywrightTestConfig = {
	webServer: {
		command: 'npm run gragBuild && npm run preview',
		port: 4173
	},
	testDir: 'tests',
	testMatch: /(.+\.)?(test|spec)\.[jt]s/
};

export default config;


