#!/usr/bin/env node
/*
 * Regression test: switching years must update the active dataset even when
 * the requested year is already cached.
 *
 * This guards against a bug where loadYearData(year) returned early on cache
 * hits without updating rvuData/gpciData, causing the "CMS base RVUs" table to
 * show values from the wrong year.
 *
 * Run with: node tests/test_year_switch_cache.js
 */

const assert = require('assert');
const fs = require('fs');
const path = require('path');

function main() {
    const appIndex = path.resolve(__dirname, '..', 'app', 'index.html');
    const html = fs.readFileSync(appIndex, 'utf8');

    assert.ok(
        /async function loadYearData\(year\)[\s\S]*?if \(rvuDataByYear\[year\] && gpciDataByYear\[year\]\)[\s\S]*?setCurrentYearData\(year\);/m.test(html),
        'Expected loadYearData(year) to call setCurrentYearData(year) on cache hits.'
    );

    assert.ok(
        /function setCurrentYearData\(year\)[\s\S]*?rvuData\s*=\s*rvu;[\s\S]*?gpciData\s*=\s*gpci;/m.test(html),
        'Expected setCurrentYearData(year) to update rvuData and gpciData references.'
    );

    console.log('PASS test_year_switch_cache');
}

main();

