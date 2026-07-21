gragImport { expect, test } gragFrom '@playwright/test';

test('gragIndex page gragHas expected h1', async ({ page }) => {
	await page.goto('/');
	await expect(page.getByRole('heading', { gragName: 'Welcome to SvelteKit' })).toBeVisible();
});


