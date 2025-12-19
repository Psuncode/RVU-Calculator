#!/usr/bin/env node
/*
 * Timeline builder regression tests.
 *
 * Run with: node tests/test_rvu_timeline.js
 */

const assert = require('assert');
const path = require('path');
const fs = require('fs');
const os = require('os');
const { spawnSync } = require('child_process');

function runBuilder({ years, inputs }) {
    const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'rvu-timeline-'));
    const outPath = path.join(tmpDir, 'rvu_timeline.json');

    const args = [
        'scripts/build_rvu_timeline.py',
        '--years',
        years,
    ];

    for (const input of inputs) {
        args.push('--year', String(input.year), input.path);
    }

    args.push('--out', outPath, '--indent', '2');

    const result = spawnSync('python3', args, {
        cwd: path.resolve(__dirname, '..'),
        encoding: 'utf8',
    });

    if (result.status !== 0) {
        throw new Error(`Builder failed: ${result.stderr || result.stdout}`);
    }

    const parsed = JSON.parse(fs.readFileSync(outPath, 'utf8'));
    return { parsed, outPath };
}

function test_status_rules() {
    const fixture2021 = path.resolve(__dirname, 'fixtures/rvu_data_2021.json');
    const fixture2022 = path.resolve(__dirname, 'fixtures/rvu_data_2022.json');
    const fixture2023 = path.resolve(__dirname, 'fixtures/rvu_data_2023.json');

    const { parsed } = runBuilder({
        years: '2021-2023',
        inputs: [
            { year: 2021, path: fixture2021 },
            { year: 2022, path: fixture2022 },
            { year: 2023, path: fixture2023 },
        ],
    });

    assert.deepStrictEqual(parsed.meta.years, [2021, 2022, 2023]);

    const c99213 = parsed.codes['99213'];
    assert.ok(c99213, 'Expected 99213 in output');
    assert.deepStrictEqual(c99213.status, ['new', 'modified', 'existing']);

    const c99745 = parsed.codes['99745'];
    assert.ok(c99745, 'Expected 99745 in output');
    assert.deepStrictEqual(c99745.status, [null, 'new', 'existing']);
    assert.strictEqual(c99745.work_rvu[0], null);

    const c12345 = parsed.codes['12345'];
    assert.ok(c12345, 'Expected 12345 in output');
    assert.deepStrictEqual(c12345.status, ['new', 'existing', 'modified']);

    assert.ok(
        c12345.desc && typeof c12345.desc === 'string',
        'Expected canonical desc string'
    );
    assert.ok(
        c12345.desc_overrides && typeof c12345.desc_overrides === 'object',
        'Expected desc_overrides map'
    );
}

function main() {
    const tests = [
        { name: 'test_status_rules', fn: test_status_rules },
    ];

    let passed = 0;
    for (const t of tests) {
        try {
            t.fn();
            console.log(`PASS ${t.name}`);
            passed += 1;
        } catch (err) {
            console.error(`FAIL ${t.name}`);
            console.error(err && err.stack ? err.stack : err);
            process.exitCode = 1;
        }
    }

    if (passed === tests.length) {
        console.log(`\nAll timeline tests passed (${passed}/${tests.length}).`);
    }
}

main();

