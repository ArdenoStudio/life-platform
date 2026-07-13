import { expect, test } from '@playwright/test'

async function hasHorizontalOverflow(page: import('@playwright/test').Page) {
  return page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 2)
}

test('page=today alias loads District Life Pulse', async ({ page }) => {
  const overviewResponse = page.waitForResponse(
    (response) => response.url().includes('/life/overview') && response.status() === 200,
    { timeout: 20000 },
  )
  await page.goto('/?page=today&locale=en', { waitUntil: 'domcontentloaded' })
  await overviewResponse

  await expect(page.getByText(/District Life Pulse/i)).toBeVisible({ timeout: 15000 })

  await expect(page.getByText('Cost of Life', { exact: true })).toBeVisible()
  await expect(page.getByText(/\d+\/100|LKR|Rs\./).first()).toBeVisible()

  await expect(page.getByText('Trust release', { exact: true })).toBeVisible()
  const degradationBanner = page.getByText(/Some signals are degraded/i)
  const trustReleaseBadge = page.getByText(/Promoted release|Seed fallback/i).first()
  await expect(degradationBanner.or(trustReleaseBadge)).toBeVisible()

  expect(await hasHorizontalOverflow(page)).toBe(false)
})

test('district change updates URL', async ({ page }) => {
  await page.goto('/?page=today&locale=en', { waitUntil: 'domcontentloaded' })
  await expect(page.getByText(/District Life Pulse/i)).toBeVisible({ timeout: 15000 })

  await page.getByLabel('Home district').selectOption('Kandy')
  await expect.poll(() => page.url()).toMatch(/page=today/)
  await expect.poll(() => page.url()).toContain('district=Kandy')
})

test('sister view-on-platform deep link carries Ariva UTM', async ({ page }) => {
  const overviewResponse = page.waitForResponse(
    (response) => response.url().includes('/life/overview') && response.status() === 200,
    { timeout: 20000 },
  )
  await page.goto('/?page=today&locale=en', { waitUntil: 'domcontentloaded' })
  await overviewResponse

  const platformLink = page.getByRole('link', { name: /View on/i }).first()
  await expect(platformLink).toBeVisible({ timeout: 15000 })
  await expect(platformLink).toHaveAttribute('href', /utm_source=ariva_life_pulse/)

  const popupPromise = page.waitForEvent('popup', { timeout: 5000 }).catch(() => null)
  await platformLink.click()
  const popup = await popupPromise
  if (popup) {
    await popup.close()
  }
})

test('decide page loads with compare params', async ({ page }) => {
  const affordabilityResponse = page.waitForResponse(
    (response) => response.url().includes('/life/affordability') && response.status() === 200,
    { timeout: 20000 },
  )
  await page.goto('/?page=decide&district=Colombo&compare=Kandy&profile=family&locale=en', {
    waitUntil: 'domcontentloaded',
  })
  await affordabilityResponse

  await expect(page.getByRole('heading', { name: 'Cost comparison', exact: true })).toBeVisible({ timeout: 15000 })
  await expect(page.getByLabel('Compare against')).toHaveValue('Kandy')

  const compareTable = page.getByRole('table')
  for (const rowLabel of ['Food', 'Fuel', 'Shelter'] as const) {
    await expect(compareTable.getByText(rowLabel, { exact: true })).toBeVisible()
  }

  expect(await hasHorizontalOverflow(page)).toBe(false)
})

test('move page loads', async ({ page }) => {
  const transportResponse = page.waitForResponse(
    (response) => response.url().includes('/life/transport') && response.status() === 200,
    { timeout: 20000 },
  )
  await page.goto('/?page=move&district=Colombo&locale=en', { waitUntil: 'domcontentloaded' })
  await transportResponse

  await expect(page.getByRole('heading', { name: 'Move desk', exact: true })).toBeVisible({ timeout: 15000 })
  await expect(page.getByText('Commute and savings')).toBeVisible()
  expect(await hasHorizontalOverflow(page)).toBe(false)
})

test('Ariva home renders without horizontal overflow', async ({ page }) => {
  await page.goto('/?locale=en', { waitUntil: 'domcontentloaded' })

  await expect(page.getByText(/District Life Pulse/i)).toBeVisible({ timeout: 15000 })
  await expect(page.getByText('Ariva').first()).toBeVisible()
  await expect(page.getByText('Food', { exact: true }).first()).toBeVisible()
  await expect(page.getByText('Fuel', { exact: true }).first()).toBeVisible()
  await expect(page.getByText('Shelter', { exact: true }).first()).toBeVisible()
  await expect(page.getByRole('button', { name: 'Cost Desk', exact: true })).toBeVisible()

  expect(await hasHorizontalOverflow(page)).toBe(false)
})

test('sources and trilingual UI render without horizontal overflow', async ({ page }) => {
  await page.goto('/', { waitUntil: 'domcontentloaded' })
  await page.getByLabel(/Language/i).selectOption('si')
  await expect(page.getByText(/දිස්ත්‍රික් ජීවන තත්ත්වය/i)).toBeVisible({ timeout: 15000 })
  await page.getByLabel('Primary').getByRole('button', { name: /විශ්වාසය/i }).click()

  await expect(page.getByRole('heading', { name: 'විශ්වාසය', exact: true, level: 1 })).toBeVisible()
  await expect(page.getByText(/සියලු මූලාශ්‍ර/i)).toBeVisible()
  await expect(page.getByText(/මූලාශ්‍ර වලංගුකරණ/i)).toBeVisible()
  await expect(page.getByText(/සක්‍රීය මූලාශ්‍ර නිකුතුව/i)).toBeVisible()
  await expect(page.getByText(/Seed fallback|ප්‍රවර්ධිත නිකුතුව/i)).toBeVisible()
  await expect(page.getByText(/Score source gate/i)).toBeVisible()
  await expect(page.getByText(/ඉහළ මූලාශ්‍ර සෞඛ්‍යය/i)).toBeVisible()
  await expect(page.getByText(/සක්‍රීය මූලාශ්‍ර ලේඛනය/i)).toBeVisible()
  await expect(page.getByText('official public').first()).toBeVisible()
  await expect(page.getByText('scheduled refresh plus manual trigger').first()).toBeVisible()

  expect(await hasHorizontalOverflow(page)).toBe(false)
})

test('atlas district profile renders without horizontal overflow', async ({ page }) => {
  const atlasResponse = page.waitForResponse(
    (response) => response.url().includes('/life/atlas') && response.status() === 200,
    { timeout: 20000 },
  )
  await page.goto('/?page=atlas&district=Kandy&locale=en', { waitUntil: 'domcontentloaded' })
  await atlasResponse

  await expect(page.locator('h2').filter({ hasText: 'Kandy' })).toBeVisible({ timeout: 15000 })
  await expect(page.getByRole('heading', { name: 'Compare districts', exact: true })).toBeVisible()
  await expect(page.getByLabel('Compare against')).toBeVisible()
  await expect(page.getByText('Component gap')).toBeVisible()
  await expect(page.getByText('District profile')).toBeVisible()
  await expect(page.getByRole('cell', { name: '1,461,895' })).toBeVisible()
  await expect(page.getByText('Score methodology')).toBeVisible()

  expect(await hasHorizontalOverflow(page)).toBe(false)
})

test('cost desk exposes official tariff and import source trails', async ({ page }) => {
  const costResponse = page.waitForResponse(
    (response) => response.url().includes('/life/cost-command') && response.status() === 200,
    { timeout: 20000 },
  )
  await page.goto('/?page=cost&district=Colombo&locale=en', { waitUntil: 'domcontentloaded' })
  await costResponse

  await expect(page.getByRole('heading', { name: /LKR/i })).toBeVisible({ timeout: 15000 })
  await expect(page.getByText('pucsl-electricity').first()).toBeVisible()
  await expect(page.getByText('ntc-bus-fares').first()).toBeVisible()
  await expect(page.getByText('sri-lanka-customs-tariff').first()).toBeVisible()

  expect(await hasHorizontalOverflow(page)).toBe(false)
})

test('weather risk signal renders without horizontal overflow', async ({ page }) => {
  await page.goto('/?page=intelligence&locale=en', { waitUntil: 'domcontentloaded' })

  await expect(page.getByRole('heading', { name: 'Signals', exact: true })).toBeVisible({ timeout: 15000 })
  await expect(page.getByText('Weather and risk watch')).toBeVisible()
  await expect(page.getByText(/confidence:/i).first()).toBeVisible()
  await expect(page.getByText(/observed:/i).first()).toBeVisible()
  await expect(page.getByText('foodlk-platform').first()).toBeVisible()
  await expect(page.getByText(/Highest 3h rain/i)).toBeVisible()
  await expect(page.getByText(/Ratnapura/i).last()).toBeVisible()

  expect(await hasHorizontalOverflow(page)).toBe(false)
})

test('operator release review shell stays protected and responsive', async ({ page }) => {
  await page.goto('/?page=operator&locale=en', { waitUntil: 'domcontentloaded' })

  await expect(page.getByRole('heading', { name: 'Source release review' })).toBeVisible({ timeout: 15000 })
  await expect(page.getByRole('heading', { name: 'Official cost evidence' })).toBeVisible()
  await expect(page.getByLabel('Token')).toBeVisible()
  await expect(page.getByRole('button', { name: 'Run reviewed contract' })).toBeDisabled()
  await expect(page.getByRole('button', { name: 'Run live source check' })).toBeDisabled()
  await expect(page.getByText('Run or load the official cost evidence review.')).toBeVisible()
  await expect(page.getByText('Paste the internal token and load release evidence.')).toBeVisible()

  expect(await hasHorizontalOverflow(page)).toBe(false)
})

test('authenticated My Ariva Pulse supports save and alert actions', async ({ page }) => {
  test.skip(!process.env.LIFE_E2E_AUTH_TOKEN, 'Set LIFE_E2E_AUTH_TOKEN and VITE_LIFE_TEST_AUTH_TOKEN for authenticated smoke.')

  await page.goto('/?locale=en', { waitUntil: 'domcontentloaded' })
  await expect(page.getByRole('heading', { name: 'My Ariva Pulse' })).toBeVisible({ timeout: 15000 })
  await page.getByRole('button', { name: /Save filters/i }).click()

  await page.goto('/?page=intelligence&locale=en', { waitUntil: 'domcontentloaded' })
  await expect(page.getByRole('heading', { name: 'Signals', exact: true })).toBeVisible({ timeout: 15000 })
  await page.getByRole('button', { name: 'Save' }).first().click()
  await page.getByRole('button', { name: 'Alert' }).first().click()

  await page.getByRole('button', { name: /Today/i }).click()
  await expect(page.getByText('Saved watches', { exact: true })).toBeVisible()
  await expect(page.getByText('Active rules', { exact: true })).toBeVisible()
  expect(await hasHorizontalOverflow(page)).toBe(false)
})
