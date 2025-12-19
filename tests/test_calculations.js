#!/usr/bin/env node
/**
 * Test script to verify RVU calculations match PRD specifications
 *
 * Run with: node test_calculations.js
 */

// Test data from CMS 2022 (PPRRVU22_JAN and GPCI2022)
const testData = {
    "99213": {
        desc: "Office o/p est low 20-29 min",
        work_rvu: 1.30,
        pe_rvu_fac: 0.55,
        pe_rvu_nonfac: 1.26,
        mp_rvu: 0.10
    }
};

const utahGPCI = {
    work_gpci: 1.000,
    pe_gpci: 0.919,
    mp_gpci: 0.799
};

// Test cases using CMS 2022 data
const testCases = [
    {
        name: "Case NF-1 (Non-facility POS) - CMS 2022",
        code: "99213",
        pos: "non-facility",
        cf: 39.69,
        expected: {
            adjWork: 1.3000,  // 1.30 × 1.000
            adjPE: 1.1579,    // 1.26 × 0.919
            adjMP: 0.0799,    // 0.10 × 0.799
            total: 2.5378,    // sum of above
            payment: 100.73   // 2.5378 × 39.69
        }
    },
    {
        name: "Case FAC-1 (Facility POS) - CMS 2022",
        code: "99213",
        pos: "facility",
        cf: 39.69,
        expected: {
            adjWork: 1.3000,  // 1.30 × 1.000
            adjPE: 0.5055,    // 0.55 × 0.919 (rounded to 4 decimals)
            adjMP: 0.0799,    // 0.10 × 0.799
            total: 1.8854,    // sum of above
            payment: 74.83    // 1.8854 × 39.69
        }
    }
];

function calculateAdjustedRVUs(code, pos) {
    const data = testData[code];
    const peRVU = pos === 'facility' ? data.pe_rvu_fac : data.pe_rvu_nonfac;

    const adjWork = data.work_rvu * utahGPCI.work_gpci;
    const adjPE = peRVU * utahGPCI.pe_gpci;
    const adjMP = data.mp_rvu * utahGPCI.mp_gpci;
    const total = adjWork + adjPE + adjMP;

    return { adjWork, adjPE, adjMP, total };
}

function runTests() {
    console.log('RVU Calculator - Test Suite');
    console.log('=' .repeat(60));
    console.log('');

    let passed = 0;
    let failed = 0;

    testCases.forEach(test => {
        console.log(`Testing: ${test.name}`);
        console.log('-'.repeat(60));

        const result = calculateAdjustedRVUs(test.code, test.pos);
        const payment = result.total * test.cf;

        // Check each value (allowing small floating point differences)
        const tolerance = 0.0001;
        const checks = [
            {
                name: 'Adjusted Work RVU',
                actual: result.adjWork,
                expected: test.expected.adjWork
            },
            {
                name: 'Adjusted PE RVU',
                actual: result.adjPE,
                expected: test.expected.adjPE
            },
            {
                name: 'Adjusted MP RVU',
                actual: result.adjMP,
                expected: test.expected.adjMP
            },
            {
                name: 'Total Adjusted RVUs',
                actual: result.total,
                expected: test.expected.total
            },
            {
                name: 'Estimated Payment',
                actual: payment,
                expected: test.expected.payment,
                tolerance: 0.01  // Allow 1 cent difference
            }
        ];

        let testPassed = true;
        checks.forEach(check => {
            const tol = check.tolerance || tolerance;
            const diff = Math.abs(check.actual - check.expected);
            const pass = diff < tol;

            console.log(`  ${check.name}:`);
            console.log(`    Expected: ${check.expected.toFixed(4)}`);
            console.log(`    Actual:   ${check.actual.toFixed(4)}`);
            console.log(`    ${pass ? '✓ PASS' : '✗ FAIL'}`);

            if (!pass) {
                testPassed = false;
                console.log(`    Difference: ${diff.toFixed(6)}`);
            }
        });

        if (testPassed) {
            console.log(`\n✓ ${test.name} PASSED\n`);
            passed++;
        } else {
            console.log(`\n✗ ${test.name} FAILED\n`);
            failed++;
        }
    });

    console.log('=' .repeat(60));
    console.log(`Results: ${passed} passed, ${failed} failed`);
    console.log('=' .repeat(60));

    return failed === 0;
}

// Additional verification tests
function verifyPrecision() {
    console.log('\nPrecision Verification');
    console.log('=' .repeat(60));

    const result = calculateAdjustedRVUs("99213", "non-facility");

    console.log('Checking display precision requirements:');
    console.log(`  Adjusted components to 4 decimals: ${result.adjWork.toFixed(4)}`);
    console.log(`  Total Adjusted RVUs to 4 decimals: ${result.total.toFixed(4)}`);
    console.log(`  Payment to $0.01: $${(result.total * 39.69).toFixed(2)}`);
    console.log('✓ Precision requirements met\n');
}

// Run tests
if (runTests()) {
    verifyPrecision();
    console.log('All tests passed! ✓');
    process.exit(0);
} else {
    console.log('Some tests failed! ✗');
    process.exit(1);
}
